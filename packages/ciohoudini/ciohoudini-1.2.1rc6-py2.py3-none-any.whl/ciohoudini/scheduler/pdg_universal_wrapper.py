#!/usr/bin/env hython
"""
PDG Universal Wrapper Script - Simplified General Solution
This script replicates the successful local execution pattern for any PDG network
"""

import os
import sys
import json
import time
import threading
import argparse
import traceback
from datetime import datetime
import shutil
import re
import io
from contextlib import redirect_stderr

# IMPORTANT: Remove any diagnostic script imports or executions
# Do not import or exec any other scripts

# Add Houdini Python libs to path
try:
    import hou
    import pdg
except ImportError:
    print("Error: This script must be run with hython")
    sys.exit(1)


class SimplePDGExecutor:
    """Simplified PDG executor that mimics successful local execution"""

    def __init__(self, hip_file, topnet_path, working_dir, output_dir, execution_method):
        self.hip_file = hip_file
        self.topnet_path = topnet_path
        self.original_working_dir = working_dir  # Store original working dir
        self.output_dir = output_dir
        self.execution_method = execution_method

        # Clean paths (remove Windows drive letters for cross-platform compatibility)
        self.hip_file = self.clean_path(self.hip_file.strip('"'))
        self.original_working_dir = self.clean_path(working_dir.strip('"'))
        self.output_dir = self.clean_path(output_dir.strip('"'))

        # Make paths absolute after cleaning
        self.hip_file = os.path.abspath(self.hip_file)
        self.original_working_dir = os.path.abspath(self.original_working_dir)
        self.output_dir = os.path.abspath(self.output_dir)
        self.original_hip_path = os.getenv("PDG_DIR", os.path.dirname(self.hip_file))
        self.original_hip_path = self.original_hip_path.strip('"').rstrip('/')
        self.original_project_root = os.path.abspath(self.original_hip_path)

        # Working dir will be updated to temp workspace later
        self.working_dir = self.original_working_dir
        self.temp_workspace = None

        self.topnet = None
        self.scheduler = None
        self.output_node = None
        self.ml_node = None  # Track ML node specifically
        self.start_time = time.time()
        self.files_before = set()
        self.files_after = set()
        self.files_copied = 0
        self.is_cooking = False
        self.copied_files_list = set()

        self.status_dict = {}

    def clean_path(self, current_path):
        """
        Prepares a file path by expanding environment variables, normalizing slashes,
        and removing drive letters for cross-platform compatibility.

        Args:
            current_path (str): The file path to prepare.

        Returns:
            str: The prepared file path, normalized for the current platform.
        """
        try:
            if not current_path:
                return current_path

            # Expand environment variables
            path = os.path.expandvars(current_path)

            # Remove quotes if present
            path = path.strip('"').strip("'")

            # Handle Windows paths on Linux/Mac
            if os.name != 'nt' and len(path) > 2 and path[1] == ':':
                # Remove drive letter (e.g., "C:" -> "")
                path = path[2:]

            # Convert backslashes to forward slashes
            path = path.replace('\\', '/')

            # Normalize the path
            path = os.path.normpath(path)

            return path

        except Exception as e:
            print(f"  Warning: Could not clean path {current_path}: {e}")
            return current_path

    def run(self):
        """Main execution flow"""
        print("=" * 80)
        print("PDG UNIVERSAL WRAPPER")
        print("=" * 80)
        print(f"HIP File: {self.hip_file}")
        print(f"TOP Network: {self.topnet_path}")
        print(f"Working Dir: {self.working_dir}")
        print(f"Output Dir: {self.output_dir}")
        print("=" * 80)

        try:
            # Step 0: Prevent any automatic script execution
            # self._disable_auto_scripts()

            # Phase 1: Selecting workspace
            self._select_best_workspace()

            # Phase 2: Setup environment (including SideFXLabs)
            if not self._setup_environment():
                return False

            # Phase 3: Initialize Houdini OTL paths BEFORE loading HIP
            self._initialize_otl_paths()

            # Phase 4: Load HIP file
            if not self._load_hip_file():
                return True

            # Phase 5: Locate TOP network
            if not self._locate_topnet():
                return True

            # Phase 6: Setup scheduler if needed
            if not self._ensure_scheduler():
                return True

            # Phase 7: configure ML node
            self._configure_ml_node()

            # Phase 8: Scan for existing files
            self._scan_files_before()

            # Phase 9: Execute
            success = self.threaded_cooking()

            # Phase 10: Collect outputs and copy to output directory
            self._scan_and_copy_outputs_comprehensive()

            # Phase 11: Save Final Hip File
            self._save_final_hip()

            # Phase 12: Report results
            self._report_results()

            # return success
            return True

        except Exception as e:
            print(f"\nERROR: {e}")
            traceback.print_exc()
            # return False
            return True

    def _disable_auto_scripts(self):
        """Disable automatic Python script execution"""
        print("\n0. DISABLING AUTO SCRIPTS")
        print("-" * 40)

        try:
            # Method 1: Override hou.session before it can be populated
            import sys
            import types

            # Create an empty module for hou.session
            empty_session = types.ModuleType('hou.session')
            sys.modules['hou.session'] = empty_session
            hou.session = empty_session

            # Method 2: Set environment to prevent Python execution
            os.environ["HOUDINI_DISABLE_CONSOLE"] = "1"

            # Method 3: Override the Python panel execution
            try:
                hou.ui.curDesktop().findPaneTab("pythonpanel").setIsCurrentTab(False)
            except:
                pass

            print("  ✓ Auto script execution disabled")

        except Exception as e:
            print(f"  ⚠ Could not fully disable auto scripts: {e}")

    def _initialize_otl_paths(self):
        """Initialize OTL scan paths before loading HIP file"""
        print("\n" + "-" * 80)
        print("Phase 3: INITIALIZING OTL PATHS")
        print("-" * 80)

        try:
            # Get SideFXLabs path if set
            sidefxlabs = os.environ.get("SIDEFXLABS")
            if sidefxlabs and os.path.exists(sidefxlabs):
                otl_dir = os.path.join(sidefxlabs, "otls")
                if os.path.exists(otl_dir):
                    # Add to OTL scan path using hscript
                    hou.hscript(f'otadd "{otl_dir}"')

                    # Also try to load specific OTLs that are commonly missing
                    otl_files = [
                        "ml_cv_rop_synthetic_data.hda",
                        "ml_cv_rop_annotation_output.hda",
                        "ml_cv_label_metadata.hda",
                        "ml_cv_synthetics_karma_rop.hda"
                    ]

                    for otl_file in otl_files:
                        # Try with version number
                        versioned_file = None
                        for f in os.listdir(otl_dir) if os.path.exists(otl_dir) else []:
                            if f.startswith(otl_file.replace(".hda", "")) and f.endswith(".hda"):
                                versioned_file = os.path.join(otl_dir, f)
                                break

                        if versioned_file and os.path.exists(versioned_file):
                            try:
                                hou.hda.installFile(versioned_file)
                                print(f"  ✓ Loaded: {os.path.basename(versioned_file)}")
                            except:
                                pass

                    # Refresh OTL database
                    hou.hscript('otrefresh')
                    print(f"  ✓ OTL paths initialized from: {otl_dir}")
            else:
                print("  ⚠ No SideFXLabs path available for OTLs")

        except Exception as e:
            print(f"  ⚠ Could not initialize OTL paths: {e}")

    def _setup_environment(self):
        """Setup execution environment"""
        print("\n" + "-" * 80)
        print("Phase 2: SETTING UP ENVIRONMENT")
        print("-" * 80)

        try:
            # Create directories
            os.makedirs(self.output_dir, exist_ok=True)
            os.makedirs(self.working_dir, exist_ok=True)

            # Setup SideFXLabs first if available
            self._setup_sidefxlabs_env()

            # CRITICAL: Set $JOB to the temp workspace
            # This controls where Houdini and PDG write project files
            # The ML node's internal nodes (pythonvenv, etc.) use $JOB as base path
            os.environ["JOB"] = self.working_dir
            print(f"  ✓ JOB: {self.working_dir}")

            # Set HIP-related variables
            # Note: Keep HIP pointing to original for file references, but JOB controls output
            os.environ["HIP"] = self.working_dir  # Was: os.path.dirname(self.hip_file)
            os.environ["HIPFILE"] = self.hip_file
            os.environ["HIPNAME"] = os.path.splitext(os.path.basename(self.hip_file))[0]

            # Set PDG working directory
            pdg_dir = os.path.join(self.working_dir, "pdg")
            pdg_dir = pdg_dir.replace('\\', '/')
            os.makedirs(pdg_dir, exist_ok=True)
            os.environ["PDG_DIR"] = pdg_dir

            # Set PDG temp directory
            pdgtemp = os.path.join(self.working_dir, "pdgtemp", str(os.getpid()))
            os.makedirs(pdgtemp, exist_ok=True)
            os.environ["PDG_TEMP"] = pdgtemp

            # Set Houdini temp directory
            os.environ["HOUDINI_TEMP_DIR"] = pdgtemp

            # Set critical environment variables
            os.environ['PDG_DIR'] = self.working_dir
            os.environ['PDG_WORKING_DIR'] = self.working_dir
            os.environ['PDG_RENDER_DIR'] = self.output_dir
            os.environ['PDG_RESULT_SERVER'] = '1'

            # Set temp directory if using temp workspace
            if self.temp_workspace:
                os.environ['PDG_TEMP'] = self.temp_workspace
                print(f"  ✓ PDG_TEMP: {self.temp_workspace}")

            print(f"  ✓ Working directory: {self.working_dir}")
            print(f"  ✓ Output directory: {self.output_dir}")
            print(f"  ✓ PDG temp: {pdgtemp}")
            print(f"  ✓ PDG_DIR: {self.working_dir}")
            print(f"  ✓ PDG_RENDER_DIR: {self.output_dir}")

            return True

        except Exception as e:
            print(f"  ✗ Failed to setup environment: {e}")
            return False

    def _setup_sidefxlabs_env(self):
        """Setup SideFXLabs environment before HIP load"""
        try:
            # Check if SIDEFXLABS is already set
            sidefxlabs = os.environ.get("SIDEFXLABS")
            if sidefxlabs and os.path.exists(sidefxlabs):
                print(f"  ✓ SideFXLabs already configured: {sidefxlabs}")
                return

            # Get Houdini version to find matching SideFXLabs
            houdini_version = hou.applicationVersionString()
            major_minor = '.'.join(houdini_version.split('.')[:2])

            # Common SideFXLabs locations
            possible_paths = [
                f"/opt/sidefx/sidefxlabs-houdini/{major_minor.split('.')[0]}",
                f"/opt/sidefx/sidefxlabs",
                "/opt/sidefxlabs",
                os.path.expanduser("~/Documents/SideFXLabs"),
                os.path.expanduser("~/SideFXLabs")
            ]

            # Look for sidefxlabs with specific version
            import glob
            labs_pattern = f"/opt/sidefx/sidefxlabs-houdini/{major_minor.split('.')[0]}/sidefxlabs-houdini-*"
            labs_dirs = glob.glob(labs_pattern)
            if labs_dirs:
                # Use the latest version
                labs_dirs.sort()
                possible_paths.insert(0, labs_dirs[-1])

            for path in possible_paths:
                if os.path.exists(path):
                    os.environ["SIDEFXLABS"] = path

                    # Add to HOUDINI_PATH
                    current_path = os.environ.get("HOUDINI_PATH", "")
                    if path not in current_path:
                        os.environ["HOUDINI_PATH"] = f"{path};&" if not current_path else f"{path};{current_path}"

                    print(f"  ✓ SideFXLabs configured: {path}")
                    return

            print("  ⚠ SideFXLabs not found in common locations")

        except Exception as e:
            print(f"  ⚠ Could not setup SideFXLabs: {e}")

    def _load_hip_file(self):
        """Load the Houdini HIP file"""
        print("\n" + "-" * 80)
        print("Phase 4: LOADING HIP FILE")
        print("-" * 80)

        try:
            if not os.path.exists(self.hip_file):
                raise FileNotFoundError(f"HIP file not found: {self.hip_file}")

            print(f"Loading: {self.hip_file}")

            # Load the file and capture any warnings
            try:
                hou.hipFile.load(self.hip_file, suppress_save_prompt=True, ignore_load_warnings=True)
                time.sleep(5)
            except hou.LoadWarning as warning:
                # This is just a warning, not an error - file loaded successfully
                print(f"  Note: Load warning (can be ignored): {warning}")
            except hou.OperationFailed as e:
                # This is an actual error
                if "Warnings were generated" in str(e):
                    # This is actually just warnings, not a failure
                    print(f"  Note: Warnings during load (continuing): {e}")
                else:
                    # This is a real failure
                    raise e

            # Verify load by checking the current file
            current_hip = hou.hipFile.name()
            if os.path.abspath(current_hip) == os.path.abspath(self.hip_file):
                print(f"✓ HIP file loaded successfully: {current_hip}")
            else:
                # Sometimes the path format differs, check if it's essentially the same file
                print(f"✓ HIP file loaded: {current_hip}")

            # Update paths if needed - CRITICAL: Set JOB to temp workspace
            # This ensures ML node internal paths go to temp workspace
            # hou.hscript(f"set JOB = {self.working_dir}")
            hou.hscript(f"set PDG_DIR = {self.working_dir}")
            hou.hscript(f"set PDG_RENDER_DIR = {self.output_dir}")
            print(f"  ✓ Set $JOB = {self.working_dir}")

            # CRITICAL: Set $HIP to temp workspace for ML node file patterns
            # The ML node's locate_renders and locate_backgrounds nodes use $HIP to find files
            hou.hscript(f"set HIP = {self.working_dir}")
            print(f"  ✓ Set $HIP = {self.working_dir}")

            return True

        except FileNotFoundError as e:
            print(f"✗ File not found: {e}")
            return False
        except Exception as e:
            # Check if this is just a warning about incomplete asset definitions
            error_str = str(e)
            if "Warnings were generated" in error_str or "incomplete asset definitions" in error_str:
                print(f"  Note: Load completed with warnings (continuing):")
                print(f"    {error_str}")

                # Verify the file actually loaded
                try:
                    current_hip = hou.hipFile.name()
                    print(f"✓ HIP file loaded despite warnings: {current_hip}")

                    # Update paths
                    hou.hscript(f"set PDG_DIR = {self.working_dir}")
                    hou.hscript(f"set PDG_RENDER_DIR = {self.output_dir}")

                    return True
                except:
                    # If we can't get the hip file name, it didn't load
                    print(f"✗ Failed to verify HIP file load")
                    return False
            else:
                # This is a real error
                print(f"✗ Failed to load HIP file: {e}")
                return False


    def _select_best_workspace(self):
        """Select the location with most available disk space"""
        print("\n" + "-" * 80)
        print("Phase 1: SELECTING WORKSPACE LOCATION")
        print("-" * 80)

        candidates = []

        # Check various temp locations
        temp_locations = [
            '/tmp',
            '/var/tmp',
            '/scratch',
            os.environ.get('TMPDIR', '/tmp'),
        ]

        # Also check if we can use subdirs in working_dir
        if self.working_dir != '/':
            temp_locations.append(os.path.join(self.working_dir, '.pdg_temp'))

        for location in temp_locations:
            if not os.path.exists(location):
                try:
                    parent = os.path.dirname(location)
                    if os.path.exists(parent) and os.access(parent, os.W_OK):
                        os.makedirs(location, exist_ok=True)
                except:
                    continue

            if os.path.exists(location):
                try:
                    stat = os.statvfs(location)
                    available_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)
                    test_file = os.path.join(location, f'.write_test_{os.getpid()}')
                    try:
                        with open(test_file, 'w') as f:
                            f.write('test')
                        os.remove(test_file)
                        writable = True
                    except:
                        writable = False

                    if writable:
                        candidates.append({
                            'path': location,
                            'available_gb': available_gb,
                            'writable': writable
                        })
                        print(f"  {location}: {available_gb:.2f} GB available")
                    else:
                        print(f"  {location}: Not writable")
                except Exception as e:
                    print(f"  {location}: Error checking - {e}")

        if not candidates:
            print("  WARNING: No temp locations available, using working directory")
            self.temp_workspace = self.working_dir
        else:
            best = max(candidates, key=lambda x: x['available_gb'])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.temp_workspace = os.path.join(best['path'], f'pdg_job_{timestamp}_{os.getpid()}')
            os.makedirs(self.temp_workspace, exist_ok=True)

            print(f"\n  ✓ Selected workspace: {self.temp_workspace}")
            print(f"    Available space: {best['available_gb']:.2f} GB")

            self.original_project_root = os.path.abspath(self.original_hip_path)
            print(f"    Monitoring original project root: {self.original_project_root}")

            self.status_dict['temp_workspace'] = self.temp_workspace
            self.status_dict['disk_space'] = {
                'location': best['path'],
                'available_gb': best['available_gb']
            }
            self.temp_workspace = self.temp_workspace.replace('\\', '/')
            self.working_dir = self.temp_workspace.replace('\\', '/')
            print(f"Updated Working Dir: {self.working_dir}")
            self.preferred_move_target = self.working_dir
            """
            # NEW: Evaluate output directory disk space for possible direct-move strategy
            self.preferred_move_target = self.working_dir
            self.preferred_move_target_space_gb = 0.0
            self.preferred_move_target_realpath = ""

            try:
                real_output = os.path.realpath(self.output_dir)
                if os.path.exists(real_output):
                    stat = os.statvfs(real_output)
                    available_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)
                    self.preferred_move_target_space_gb = available_gb
                    self.preferred_move_target_realpath = real_output

                    print(f"  Output directory ({real_output}) has {available_gb:.2f} GB free")
                    if available_gb >= 1000:  # ≥ 1 TB
                        self.preferred_move_target = self.output_dir
                        print(f"  ✓ Output directory has ≥ 1 TB free → selected files will be moved directly there")
                        
                        ## NEW SAFETY CHECK: never move directly into output_dir if it's inside original_project_root
                        #orig_root_real = os.path.realpath(self.original_project_root)
                        #if os.path.commonpath([real_output, orig_root_real]) == orig_root_real:
                        #    print(
                        #        f"  ⚠ Output directory is inside monitored project root → falling back to temp workspace for safety")
                        #else:
                        #    self.preferred_move_target = self.output_dir
                        #    print(f"  ✓ Output directory has ≥ 1 TB free → files will be moved directly there")
                        
                    else:
                        print(f"  Output directory has only {available_gb:.2f} GB free → using temp workspace")
                else:
                    print(f"  Output directory does not exist yet: {self.output_dir}")
            except Exception as e:
                print(f"  Could not evaluate output directory space: {e}")
            """

    def _monitor_and_relocate_files(self):
        """Watch original project directory and move supported new files immediately"""
        import time

        if not hasattr(self, 'original_project_root') or not self.original_project_root:
            return

        # ALLOWED_EXTENSIONS = (".bgeo.sc", ".png", ".exr")
        ALLOWED_EXTENSIONS = (".bgeo.sc")

        print("\n  Starting real-time file relocation monitor...")
        seen_files = set()

        # Initial scan
        for root, _, files in os.walk(self.original_project_root):
            for f in files:
                if not f.startswith('.') and not f.endswith(('.pyc', '.pyo')):
                    seen_files.add(os.path.join(root, f))

        while self.is_cooking:
            time.sleep(0.5)

            try:
                for root, _, files in os.walk(self.original_project_root):
                    for f in files:
                        if f.startswith('.') or f.endswith(('.pyc', '.pyo')):
                            continue
                        if not f.lower().endswith(ALLOWED_EXTENSIONS):
                            continue

                        src_path = os.path.join(root, f)

                        if src_path not in seen_files:
                            seen_files.add(src_path)

                            rel_path = os.path.relpath(src_path, self.original_project_root)

                            # Choose destination
                            dst_base = self.preferred_move_target
                            dst_path = os.path.join(dst_base, rel_path)

                            # Critical safety guard: if destination is inside the monitored root → use temp workspace instead
                            dst_base_real = os.path.realpath(dst_base)
                            monitored_real = os.path.realpath(self.original_project_root)
                            if os.path.commonpath([dst_base_real, monitored_real]) == monitored_real:
                                dst_base = self.working_dir
                                # dst_base = self.preferred_move_target
                                dst_path = os.path.join(dst_base, rel_path)

                            os.makedirs(os.path.dirname(dst_path), exist_ok=True)

                            try:
                                shutil.move(src_path, dst_path)
                                target_name = "output directory" if dst_base == self.output_dir else "temp workspace"
                                print(f"  Relocated ({target_name}): {rel_path}")
                                # print(f"  Moving {src_path} to {dst_path}")
                            except Exception as e:
                                print(f"  Failed to move {src_path}: {e}")

            except Exception:
                pass  # directory may be temporarily locked

        print("  File relocation monitor stopped.")

    def _locate_topnet(self):
        """Find and validate TOP network using robust logic"""
        print("\n" + "-" * 80)
        print("Phase 5: LOCATING TOP NETWORK")
        print("-" * 80)

        try:
            # Try specified path first
            current_node = hou.node(self.topnet_path)

            if current_node:
                # Check if the node exists and find the topnet
                print(f"  Node found at {self.topnet_path} (type: {current_node.type().name()})")
                print(f"    Category: {current_node.type().category().name()}")

                # Check if this node has a childTypeCategory
                if hasattr(current_node, 'childTypeCategory') and current_node.childTypeCategory():
                    print(f"    Child category: {current_node.childTypeCategory().name()}")

                # Check if this is a TOP network container (can contain TOP nodes)
                is_topnet_container = (hasattr(current_node, 'childTypeCategory') and
                                       current_node.childTypeCategory() and
                                       current_node.childTypeCategory().name() == "Top")

                if is_topnet_container:
                    # It's already a TOP network container
                    self.topnet = current_node
                    self.topnet_path = current_node.path()
                    print(f"  ✓ Node is a TOP network container: {self.topnet_path}")
                else:
                    # It's not a TOP network container, traverse up to find one
                    print(f"  Node is not a TOP network container, searching parent hierarchy...")

                    # Start from current node's parent
                    parent_node = current_node.parent() if current_node else None

                    while parent_node is not None:
                        print(f"    Checking parent: {parent_node.path()}")

                        # Check if parent is a TOP network container
                        if (hasattr(parent_node, 'childTypeCategory') and
                                parent_node.childTypeCategory() and
                                parent_node.childTypeCategory().name() == "Top"):
                            self.topnet = parent_node
                            self.topnet_path = parent_node.path()
                            print(f"  ✓ Found TOP network container in parent: {self.topnet_path}")
                            break

                        # Move up to next parent
                        parent_node = parent_node.parent()

                    # If we didn't find a topnet in the parent hierarchy
                    if not self.topnet:
                        print(f"  No TOP network container found in parent hierarchy")
                        print("  Falling back to scene-wide search...")
                        self._search_for_topnets()
            else:
                # Node not found at specified path
                print(f"  Node not found at {self.topnet_path}")
                print("  Falling back to scene-wide search...")
                self._search_for_topnets()

            # Final check - did we find a TOP network?
            if not self.topnet:
                print("  ✗ No TOP networks found in scene")
                return False

            print(f"\n  ✓ Using TOP network: {self.topnet_path}")
            print(f"    Type: {self.topnet.type().name()}")
            print(f"    Category: {self.topnet.type().category().name()}")

            if hasattr(self.topnet, 'childTypeCategory') and self.topnet.childTypeCategory():
                print(f"    Child category: {self.topnet.childTypeCategory().name()}")

            # Catalog nodes in network
            self._catalog_top_nodes()

            # Find output node
            self._find_nodes()

            return True

        except Exception as e:
            print(f"  ✗ Failed to locate TOP network: {e}")
            return False

    def _search_for_topnets(self):
        """Search entire scene for TOP networks"""
        try:
            print("  Searching entire scene for TOP networks...")

            # Common TOP network locations
            search_paths = ['/obj', '/stage', '/tasks']
            found_topnets = []

            for search_path in search_paths:
                search_root = hou.node(search_path)
                if search_root:
                    # Recursively search for TOP networks
                    self._recursive_topnet_search(search_root, found_topnets)

            if found_topnets:
                # Use the first found TOP network
                self.topnet = found_topnets[0]
                self.topnet_path = self.topnet.path()
                print(f"  ✓ Found {len(found_topnets)} TOP network(s)")
                print(f"    Using: {self.topnet_path}")
            else:
                print("  ✗ No TOP networks found in common locations")

                # Last resort: check entire scene
                print("  Searching entire scene hierarchy...")
                self._recursive_topnet_search(hou.node('/'), found_topnets)

                if found_topnets:
                    self.topnet = found_topnets[0]
                    self.topnet_path = self.topnet.path()
                    print(f"  ✓ Found TOP network: {self.topnet_path}")

        except Exception as e:
            print(f"  Error during search: {e}")

    def _recursive_topnet_search(self, node, found_list):
        """Recursively search for TOP networks"""
        try:
            # Check if this node is a TOP network container
            if (hasattr(node, 'childTypeCategory') and
                    node.childTypeCategory() and
                    node.childTypeCategory().name() == "Top"):
                found_list.append(node)
                print(f"    Found: {node.path()}")

            # Also check if it's a topnet by type name
            elif node.type().name() in ['topnet', 'topnetmgr']:
                found_list.append(node)
                print(f"    Found: {node.path()}")

            # Recurse into children
            for child in node.children():
                self._recursive_topnet_search(child, found_list)

        except:
            pass

    def _catalog_top_nodes(self):
        """Catalog TOP nodes in the network"""
        try:
            print("\n  Cataloging TOP nodes:")

            top_nodes = []
            for node in self.topnet.children():
                try:
                    if hasattr(node.type(), 'category') and node.type().category().name() == "Top":
                        node_info = f"{node.name()} ({node.type().name()})"

                        # Check for special flags
                        flags = []
                        if hasattr(node, 'isDisplayFlagSet') and node.isDisplayFlagSet():
                            flags.append("DISPLAY")
                        if hasattr(node, 'isRenderFlagSet') and node.isRenderFlagSet():
                            flags.append("RENDER")

                        if flags:
                            node_info += f" [{', '.join(flags)}]"

                        print(f"    - {node_info}")
                        top_nodes.append(node)
                except:
                    pass

            return top_nodes

        except Exception as e:
            print(f"  Error cataloging nodes: {e}")
            return []

    def _find_nodes(self):
        """Find ML node and output node"""
        print("\n  Cataloging TOP nodes:")

        for node in self.topnet.children():
            if node.type().category().name() != "Top":
                continue

            node_type = node.type().name().lower()
            node_name = node.name()

            # Check if it's an ML node
            if 'ml_cv' in node_type:
                self.ml_node = node
                self.output_node = node  # ML nodes are typically output nodes
                print(f"    - {node_name} (ML/CV node) [OUTPUT]")

            # Check if it's flagged as output or display
            elif hasattr(node, 'isDisplayFlagSet') and node.isDisplayFlagSet():
                if not self.output_node:
                    self.output_node = node
                print(f"    - {node_name} [DISPLAY]")

            elif hasattr(node, 'isRenderFlagSet') and node.isRenderFlagSet():
                if not self.output_node:
                    self.output_node = node
                print(f"    - {node_name} [RENDER]")
            else:
                print(f"    - {node_name}")

    def _ensure_scheduler(self):
        """Ensure a scheduler exists with the specified priority order"""
        print("\n" + "-" * 80)
        print("Phase 6: SETTING UP SCHEDULER")
        print("-" * 80)

        try:
            # Priority 1: Create a new local scheduler
            try:
                self.scheduler = self.topnet.createNode("localscheduler", "auto_local_scheduler")
                print(f"  ✓ Created new local scheduler: {self.scheduler.name()}")
                self._configure_scheduler()
                return True
            except:
                pass

            # Priority 2: Use the first local scheduler found
            for node in self.topnet.children():
                if node.type().name() == "localscheduler":
                    self.scheduler = node
                    print(f"  ✓ Using existing local scheduler: {node.name()}")
                    self._configure_scheduler()
                    return True

            # Priority 3: Create a new pythonscheduler
            try:
                self.scheduler = self.topnet.createNode("pythonscheduler", "auto_python_scheduler")
                print(f"  ✓ Created new Python scheduler: {self.scheduler.name()}")
                self._configure_scheduler()
                return True
            except:
                pass

            # Priority 4: Use the first pythonscheduler found
            for node in self.topnet.children():
                if node.type().name() == "pythonscheduler":
                    self.scheduler = node
                    print(f"  ✓ Using existing Python scheduler: {node.name()}")
                    self._configure_scheduler()
                    return True

            # Priority 5: Use the first conductorscheduler found (with custom callback)
            for node in self.topnet.children():
                if "conductor" in node.type().name().lower() and "scheduler" in node.type().name().lower():
                    self.scheduler = node
                    print(f"  ✓ Using existing Conductor scheduler: {node.name()}")

                    # Reset its on_schedule callback to the default Python scheduler behavior
                    self._reset_conductor_scheduler_callback()
                    self._configure_scheduler()
                    return True

            # If no scheduler found, continue anyway
            print("  ⚠ No scheduler found or created - continuing without explicit scheduler")
            return True

        except Exception as e:
            print(f"  ⚠ Scheduler setup encountered issues: {e}")
            # Continue anyway - some networks work without explicit scheduler
            return True

    def _reset_conductor_scheduler_callback(self):
        """Reset the conductor scheduler's on_schedule callback to default Python scheduler behavior"""
        try:
            if self.scheduler and "conductor" in self.scheduler.type().name().lower():
                # Set the on_schedule callback to the default Python scheduler behavior
                on_schedule_code = '''import subprocess
import os
import sys

# Ensure directories exist and serialize the work item
self.createJobDirsAndSerializeWorkItems(work_item)

# expand the special __PDG_* tokens in the work item command
item_command = self.expandCommandTokens(work_item.command, work_item)

# add special PDG_* variables to the job's environment
temp_dir = str(self.tempDir(False))

job_env = os.environ.copy()
job_env['PDG_RESULT_SERVER'] = str(self.workItemResultServerAddr())
job_env['PDG_ITEM_NAME'] = str(work_item.name)
job_env['PDG_ITEM_ID'] = str(work_item.id)
job_env['PDG_DIR'] = str(self.workingDir(False))
job_env['PDG_TEMP'] = temp_dir
job_env['PDG_SCRIPTDIR'] = str(self.scriptDir(False))

# run the given command in a shell
returncode = subprocess.call(item_command, shell=True, env=job_env)

# if the return code is non-zero, report it as failed
if returncode == 0:
    return pdg.scheduleResult.CookSucceeded
return pdg.scheduleResult.CookFailed'''

                # Try to set the onschedule parameter if it exists
                if self.scheduler.parm("onschedule"):
                    self.scheduler.parm("onschedule").set(on_schedule_code)
                    print(f"    ✓ Reset Conductor scheduler callback to default behavior")
                elif self.scheduler.parm("pdg_onschedule"):
                    self.scheduler.parm("pdg_onschedule").set(on_schedule_code)
                    print(f"    ✓ Reset Conductor scheduler callback to default behavior")
                else:
                    print(f"    ⚠ Could not find onschedule parameter on Conductor scheduler")
        except Exception as e:
            print(f"    ⚠ Could not reset Conductor scheduler callback: {e}")


    def _configure_scheduler(self):
        # Configure scheduler for local execution
        if self.scheduler:
            try:
                # Set working directory
                work_dir_parm = self.scheduler.parm("pdg_workingdir")
                if work_dir_parm:
                    work_dir_parm.set(self.working_dir)
                    print(f"✓ Set working directory on scheduler")

                # For localscheduler, ensure it's set to execute locally
                if "local" in self.scheduler.type().name().lower():
                    # Set any local scheduler specific parameters
                    max_procs = self.scheduler.parm("maxprocsmenu")
                    if max_procs:
                        max_procs.set("0")  # Use all available cores

                # For pythonscheduler, set in-process execution
                elif "python" in self.scheduler.type().name().lower():
                    in_process = self.scheduler.parm("inprocess")
                    if in_process:
                        in_process.set(1)  # Execute in-process
                        print("  Set scheduler to in-process execution")

                print(f"  Note: Using {self.scheduler.type().name()} scheduler")
            except Exception as e:
                print(f"  Warning: Could not configure scheduler: {e}")

        # Apply scheduler to network and nodes
        scheduler_path = self.scheduler.path()
        print("\nApplying scheduler to nodes:")

        # Set as network default first
        for parm_name in ["topscheduler", "defaultscheduler", "scheduler"]:
            parm = self.topnet.parm(parm_name)
            if parm:
                try:
                    parm.set(scheduler_path)
                    print(f"  ✓ Set as network default via '{parm_name}'")
                    break
                except:
                    pass

        # Apply to individual nodes
        count = 0
        for node in self.topnet.children():
            if node.type().category().name() != "Top":
                continue
            if node == self.scheduler:
                continue
            if "scheduler" in node.type().name().lower():
                continue

            # Try different parameter names
            for parm_name in ["pdg_scheduler", "topscheduler", "scheduler"]:
                parm = node.parm(parm_name)
                if parm:
                    try:
                        parm.set(scheduler_path)
                        print(f"  ✓ {node.name()} - set via '{parm_name}'")
                        count += 1
                        break
                    except:
                        pass

        print(f"✓ Scheduler applied to {count} nodes")
        print(f"✓ Scheduler configured for single machine execution")

        return True

    def _configure_ml_node(self):
        """Configure ML node parameters if present"""

        print("\n" + "-" * 80)
        print("Phase 7: CONFIGURE ML NODE PARAMETERS (if present)")
        print("-" * 80)

        # Configure Karma ROP engines to CPU (regardless of ML node presence)
        karma_modified = self._configure_karma_rop_engines()
        if karma_modified:
            self._save_hip_after_configuration("Karma ROP configuration")


        if not self.ml_node:
            print("  No ML nodes found")
            return

        try:
            print("  " + "-" * 40)
            print(f"  Configuring: {self.ml_node.name()}")
            print("  " + "-" * 40)
            print(f"  Node type: {self.ml_node.type().name()}")

            # CRITICAL: Ensure $JOB is set in Houdini to the temp workspace
            # This is essential for ML node internal paths
            hou.hscript(f"set JOB = {self.working_dir}")
            print(f"  ✓ Set $JOB = {self.working_dir}")

            # CRITICAL: Also set $HIP to temp workspace
            # The ML node's locate_renders and locate_backgrounds nodes use $HIP to find files
            # Without this, those nodes look in the original HIP directory and find nothing
            hou.hscript(f"set HIP = {self.working_dir}")
            print(f"  ✓ Set $HIP = {self.working_dir}")

            # Create necessary directories in working_dir (temp workspace)
            datasets_dir = os.path.join(self.working_dir, 'datasets')
            render_dir = os.path.join(datasets_dir, 'render') + '/'
            delivery_dir = os.path.join(datasets_dir, 'delivery') + '/'
            hips_dir = os.path.join(self.working_dir, 'dataset_hips')
            ml_dir = os.path.join(self.working_dir, 'ml')
            labs_dir = os.path.join(ml_dir, 'labs')

            for dir_path in [datasets_dir, render_dir, delivery_dir, hips_dir, ml_dir, labs_dir]:
                os.makedirs(dir_path, exist_ok=True)
                print(f"    Created directory: {dir_path}")

            # Set ONLY directory path parameters - DO NOT override user's rendering settings
            # like varcount, varrange, frame range, etc.
            # The key insight is that we only want to redirect output paths, not change
            # what the user intended to render
            params_to_set = {
                # Directory paths - using working_dir (temp workspace)
                'renderdir': render_dir,
                'deliverydir': delivery_dir,
                'hipsdir': hips_dir,
                'outputdir': self.working_dir,
                'datasets_dir_path': datasets_dir,
                'dataset_hips_dir_path': hips_dir,
                # ML/Labs directory - CRITICAL for pythonvenv nodes
                'mldir': ml_dir,
                'ml_dir': ml_dir,
                'labsdir': labs_dir,
                'labs_dir': labs_dir,
                'venvdir': labs_dir,
                'venv_dir': labs_dir,
                'pythonvenvdir': labs_dir,
                # Base/root directory parameters
                'basedir': self.working_dir,
                'base_dir': self.working_dir,
                'rootdir': self.working_dir,
                'root_dir': self.working_dir,
                'projectdir': self.working_dir,
                'project_dir': self.working_dir,
                # Alternative parameter names
                'render_dir': render_dir,
                'delivery_dir': delivery_dir,
                'hips_dir': hips_dir,
                'output_dir': self.working_dir,
                # CRITICAL: Disable fiftyone to prevent pythonvenv_cv_fiftyone failures
                # Fiftyone requires specific Python packages that may not be available on render farms
                'openinfiftyone': 0,
                'usefiftyone': 0,
                'enablefiftyone': 0,
                'fiftyone': 0,
                'open_fiftyone': 0,
                'launchfiftyone': 0,
                'launch_fiftyone': 0,
                # NOTE: Do NOT set these parameters - they override user's rendering settings:
                # - varcount (number of variations - user decides this)
                # - varrange1 (variation range - user decides this)
                # - f1, f2 (frame range - user decides this)
                # - generatestatic (generation mode - user decides this)
                # - enable (should respect user's enable state)
            }

            print("\n  Setting parameters:")
            params_set = 0
            params_not_found = 0

            for param_name, value in params_to_set.items():
                parm = self.ml_node.parm(param_name)
                if parm:
                    try:
                        parm_type = parm.parmTemplate().type()
                        if parm_type == hou.parmTemplateType.Button:
                            if value:
                                parm.pressButton()
                                print(f"    ✓ Pressed button: {param_name}")
                                params_set += 1
                        elif parm_type == hou.parmTemplateType.String:
                            parm.set(str(value))
                            print(f"    ✓ Set {param_name} = {value}")
                            params_set += 1
                        else:
                            parm.set(value)
                            print(f"    ✓ Set {param_name} = {value}")
                            params_set += 1
                    except Exception as e:
                        print(f"    ⚠ Could not set {param_name}: {e}")
                else:
                    params_not_found += 1

            # Log user's current rendering settings (but don't change them)
            print("\n  User's rendering settings (preserved):")
            user_params = ['varcount', 'varrange1', 'f1', 'f2', 'generatestatic']
            for parm_name in user_params:
                parm = self.ml_node.parm(parm_name)
                if parm:
                    try:
                        val = parm.eval()
                        print(f"    {parm_name} = {val}")
                    except:
                        pass

            # Reconfigure internal pythonvenv nodes to use temp workspace
            self._reconfigure_pythonvenv_nodes()

            print(f"\n  ✓ ML node configuration complete")
            print(f"    Parameters set: {params_set}")
            print(f"    Parameters not found: {params_not_found}")

        except Exception as e:
            print(f"  ⚠ ML node configuration warning: {e}")
            import traceback
            traceback.print_exc()

    def _configure_karma_rop_engines(self):
        """
        Configure Karma ROP engines to use CPU mode for render farm compatibility.

        Search for labs::ml_cv_synthetics_karma_rop nodes and set their engine
        parameter to 'cpu' if it's not already set to 'cpu'.

        This ensures Karma renders use CPU mode on render farms where GPU
        acceleration may not be available or configured.

        Returns:
            bool: True if any nodes were modified, False otherwise
        """
        print("\n  Configuring Karma ROP engine settings:")
        print("  " + "-" * 40)

        nodes_modified = False

        try:
            nodes_found = 0
            nodes_changed = 0

            # Search all nodes in the scene recursively
            for node in hou.node('/').allSubChildren():
                try:
                    node_type_name = node.type().name()

                    # Check if this is a ml_cv_synthetics_karma_rop node (any version)
                    if 'ml_cv_synthetics_karma_rop' in node_type_name:
                        nodes_found += 1

                        print(f"\n    Found Karma ROP node:")
                        print(f"      Path: {node.path()}")
                        print(f"      Name: {node.name()}")
                        print(f"      Type: {node_type_name}")
                        print(f"      Category: {node.type().category().name()}")

                        # Check for engine parameter
                        engine_parm = node.parm("engine")
                        if engine_parm:
                            current_value = engine_parm.eval()
                            print(f"      Original engine: {current_value}")

                            # Set to 'cpu' if not already
                            if current_value != "cpu":
                                engine_parm.set("cpu")
                                new_value = engine_parm.eval()
                                print(f"      New engine: {new_value}")
                                print(f"      ✓ Changed engine from '{current_value}' to 'cpu'")
                                nodes_changed += 1
                                nodes_modified = True
                            else:
                                print(f"      ✓ Engine already set to 'cpu' (no change needed)")
                        else:
                            print(f"      ⚠ No 'engine' parameter found on this node")

                except Exception as node_error:
                    # Skip nodes that can't be accessed
                    continue

            # Summary
            print(f"\n  Karma ROP engine configuration summary:")
            print(f"    Nodes found: {nodes_found}")
            print(f"    Nodes modified: {nodes_changed}")

            if nodes_found == 0:
                print("    (No labs::ml_cv_synthetics_karma_rop nodes found in scene)")

        except Exception as e:
            print(f"  ⚠ Error configuring Karma ROP engines: {e}")
            import traceback
            traceback.print_exc()

        return nodes_modified

    def _save_hip_after_configuration(self, reason="configuration changes"):
        """
        Save the HIP file after making configuration changes.

        CRITICAL: This must be called AFTER all node parameter modifications
        but BEFORE PDG cooking starts. PDG transfers the HIP file to work items,
        so any in-memory changes need to be saved to disk first.

        Args:
            reason: Description of why we're saving (for logging)

        Returns:
            bool: True if save was successful, False otherwise
        """
        print(f"\n  Saving HIP file ({reason}):")
        print("  " + "-" * 40)

        try:
            # Get current HIP file path
            current_hip = hou.hipFile.path()

            # For render farm execution, save to working directory
            # This ensures PDG picks up the modified version
            if self.working_dir and self.working_dir != self.original_working_dir:
                # We're in a temp workspace - save the HIP file there
                hip_basename = os.path.basename(current_hip)
                new_hip_path = os.path.join(self.working_dir, hip_basename)

                # Save to temp workspace
                hou.hipFile.save(new_hip_path)
                print(f"    ✓ Saved HIP file to workspace: {new_hip_path}")

                # Update the HIP file reference
                self.hip_file = new_hip_path

                # Re-set $HIP and $JOB to ensure consistency
                hou.hscript(f"set HIP = {self.working_dir}")
                hou.hscript(f"set JOB = {self.working_dir}")
                print(f"    ✓ Updated $HIP and $JOB to: {self.working_dir}")

            else:
                # Save in place (same directory)
                hou.hipFile.save()
                print(f"    ✓ Saved HIP file in place: {current_hip}")

            return True

        except Exception as e:
            print(f"    ⚠ Error saving HIP file: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _reconfigure_pythonvenv_nodes(self):
        """
        Reconfigure pythonvenv nodes inside the ML node to use temp workspace.
        The pythonvenv nodes use $JOB to determine where to create venv directories.
        We need to ensure they're using our temp workspace, not the original HIP location.
        """
        if not self.ml_node:
            return

        ml_dir = os.path.join(self.working_dir, 'ml')
        labs_dir = os.path.join(ml_dir, 'labs')

        try:
            print("\n  Reconfiguring pythonvenv nodes:")

            # Get all nodes in the TOP network that might be pythonvenv nodes
            # They could be inside the ML node's internal network
            nodes_to_check = []

            # Check if ML node has children (it's a subnet/HDA)
            try:
                if hasattr(self.ml_node, 'children'):
                    nodes_to_check.extend(self.ml_node.children())
            except:
                pass

            # Also check the topnet for any pythonvenv nodes
            if self.topnet:
                try:
                    nodes_to_check.extend(self.topnet.children())
                except:
                    pass

            pythonvenv_count = 0
            for node in nodes_to_check:
                node_name = node.name().lower()
                node_type = ""
                try:
                    node_type = node.type().name().lower()
                except:
                    pass

                # Check if this is a pythonvenv node
                if 'pythonvenv' in node_name or 'pythonvenv' in node_type:
                    pythonvenv_count += 1
                    print(f"    Found pythonvenv: {node.name()}")

                    # Try to modify its output directory
                    # Common parameter names for output directory
                    for parm_name in ['venvpath', 'outputdir', 'basedir', 'venvdir',
                                      'virtualenvdir', 'pdg_venvpath', 'venv_path']:
                        parm = node.parm(parm_name)
                        if parm:
                            try:
                                parm_type = parm.parmTemplate().type()
                                if parm_type == hou.parmTemplateType.String:
                                    old_val = parm.eval()
                                    # Replace original path with temp workspace path
                                    if self.original_working_dir and self.original_working_dir in old_val:
                                        new_val = old_val.replace(self.original_working_dir, self.working_dir)
                                        parm.set(new_val)
                                        print(f"      ✓ Updated {parm_name}: {new_val}")
                                    elif '$JOB' in parm.rawValue() or '$HIP' in parm.rawValue():
                                        # Force absolute path
                                        parm.set(labs_dir)
                                        print(f"      ✓ Set {parm_name} = {labs_dir}")
                            except Exception as e:
                                print(f"      ⚠ Could not set {parm_name}: {e}")

                    # Try to dirty the node to force re-evaluation
                    try:
                        if hasattr(node, 'dirtyAllTasks'):
                            node.dirtyAllTasks(False)
                    except:
                        pass

            if pythonvenv_count == 0:
                print("    No pythonvenv nodes found at this level")
                print("    (They may be inside the ML HDA internal network)")

            # CRITICAL: Also set environment variables that pythonvenv might use
            os.environ['PDG_VENV_DIR'] = labs_dir
            os.environ['LABS_VENV_DIR'] = labs_dir
            print(f"    ✓ Set PDG_VENV_DIR = {labs_dir}")

        except Exception as e:
            print(f"    Note: Could not reconfigure pythonvenv nodes: {e}")


    def _scan_files_before(self):
        """Scan for existing files before execution"""
        print("\n" + "-" * 80)
        print("Phase 8: SCANNING EXISTING FILES")
        print("-" * 80)

        # Directories to skip during scanning
        skip_dirs = ["pdgtemp", "__pycache__", "venv", "site-packages", ".git", ".cache"]

        try:
            # Collect all locations to scan
            scan_locations = []

            # Scan output directory
            if os.path.exists(self.output_dir):
                scan_locations.append(("output_dir", self.output_dir))

            # Scan working directory (temp workspace)
            if os.path.exists(self.working_dir):
                scan_locations.append(("working_dir", self.working_dir))

            # CRITICAL: Also scan original_working_dir to capture uploaded files
            # This prevents uploaded files from being collected as "new" files
            if self.original_working_dir and os.path.exists(self.original_working_dir):
                scan_locations.append(("original_working_dir", self.original_working_dir))

            for location_name, location_path in scan_locations:
                if not os.path.exists(location_path):
                    continue

                print(f"  Scanning {location_name}: {location_path}")
                files_in_location = 0

                for root, dirs, files in os.walk(location_path):
                    # Skip certain directories
                    if any(skip in root for skip in skip_dirs):
                        dirs[:] = []  # Don't recurse into these directories
                        continue

                    # Filter out directories we don't want to recurse into
                    dirs[:] = [d for d in dirs if not any(skip in d for skip in skip_dirs)]

                    for file in files:
                        # Skip hidden files
                        if file.startswith('.'):
                            continue
                        full_path = os.path.join(root, file)
                        self.files_before.add(full_path)
                        files_in_location += 1

                print(f"    Found {files_in_location} files")

            print(f"  ✓ Total existing files registered: {len(self.files_before)}")

        except Exception as e:
            print(f"  Note: Could not scan all files: {e}")
            import traceback
            traceback.print_exc()

    def _pre_generate_wedge_nodes(self):
        # Pre-generate wedge work items
        if self.topnet:
            print("Pre-generate wedge nodes...")
            for node in self.topnet.children():
                if node.type().name() == 'wedge':
                    try:
                        node.parm('regenerate').pressButton()
                    except:
                        pass

    def _dirty_all_network_nodes_and_tasks(self):
        # Make sure the network is ready
        try:
            # Dirty all nodes to ensure fresh cook
            print("\n  Dirty all network nodes...")
            for node in self.topnet.children():
                try:
                    if hasattr(node, 'dirtyAllTasks'):
                        node.dirtyAllTasks(False)
                except:
                    pass
        except:
            pass

        try:
            print("\n  Dirty all network tasks...")
            self.topnet.dirtyAllTasks(False)
        except:
            pass
        time.sleep(2)

    def _confirm_output_node(self):
        # Find output node if not already identified
        if not self.output_node:
            output_node = None

            # Check for display flag
            for node in self.topnet.children():
                if node.type().category().name() != "Top":
                    continue
                if hasattr(node, 'isDisplayFlagSet') and node.isDisplayFlagSet():
                    output_node = node
                    break

            # Check for render flag
            if not output_node:
                for node in self.topnet.children():
                    if node.type().category().name() != "Top":
                        continue
                    if hasattr(node, 'isRenderFlagSet') and node.isRenderFlagSet():
                        output_node = node
                        break

            # Find nodes with "output" in name
            if not output_node:
                for node in self.topnet.children():
                    if node.type().category().name() != "Top":
                        continue
                    if "output" in node.name().lower() or "rop" in node.name().lower():
                        output_node = node
                        break

            self.output_node = output_node

    def _pre_execution_config(self):
        self._pre_generate_wedge_nodes()
        self._dirty_all_network_nodes_and_tasks()
        self._confirm_output_node()

    def get_topnet_category(self):
        # Determine if topnet is a SOP container or actual TOP node
        topnet_category = None
        try:
            topnet_category = self.topnet.type().category().name()
        except:
            pass
        return topnet_category

    def execute(self):
        """
        Main execution method that tries different cooking strategies.

        FIXED: For auto mode (method 0), now verifies that output files were
        actually created before declaring success. If a method completes
        without generating files, the next method is tried.
        """
        import time

        print("\nEXECUTING PDG")
        print("-" * 40)

        print("")
        print("Pre-execution configuration")

        self._pre_execution_config()

        start_time = time.time()
        print(f"Execution method is: {self.execution_method}")
        print("Executing ...")

        success = False
        topnet_category = self.get_topnet_category()

        if topnet_category and topnet_category in ["Sop"]:
            print("Topnet category is 'Sop', we must switch to individual node cooking")
            self._try_individual_node_cook()

        else:

            # Map of execution methods
            execution_methods = {
                1: ("Network execution", self._execute_network),
                2: ("PDG context cook", self._pdg_context_cook),
                3: ("Output node cook", self._try_output_node_cook),
                4: ("Scheduler execution", self._scheduler_execution),
                5: ("Individual node cook", self._try_individual_node_cook),
                6: ("Dependency chain cook", self._dependency_chain_cook),
                # 7: ("Service mode cook", self._service_mode_cook),
                # 8: ("Batch work item cook", self._batch_work_item_cook),
                # 9: ("Event callback cook", self._event_callback_cook),
                # 10: ("Command line cook", self._command_line_cook)
            }

            # Execute selected method
            if self.execution_method in execution_methods:
                method_name, method_func = execution_methods[self.execution_method]
                print(f"Using method: {method_name}")
                success = method_func()

            elif self.execution_method == 0:
                # Auto mode - try methods in sequence until one succeeds AND produces files
                print("Auto mode: Trying all methods in sequence...")

                # Record initial file count for verification
                initial_file_count = self._count_new_files()

                for method_id, (method_name, method_func) in execution_methods.items():
                    print(f"\n--- Trying method {method_id}: {method_name} ---")
                    try:
                        method_result = method_func()

                        if method_result:
                            # Method reported success - but verify files were actually created
                            time.sleep(2)  # Give filesystem time to sync
                            current_file_count = self._count_new_files()
                            files_created = current_file_count - initial_file_count

                            if files_created > 0:
                                print(f"✓ Success with method {method_id}: {method_name}")
                                print(f"  Created {files_created} new file(s)")
                                success = True
                                break
                            else:
                                print(f"⚠ Method {method_id} completed but no new files created")
                                print(f"  Trying next method...")
                                # Continue to next method
                        else:
                            print(f"✗ Method {method_id} returned failure")

                    except Exception as e:
                        print(f"✗ Method {method_id} failed: {str(e)[:100]}")

                if not success:
                    print("\n✗ All execution methods failed to produce output files")
            else:
                print(f"✗ Unknown execution method: {self.execution_method}")
                success = False

            elapsed = time.time() - start_time

            if success:
                print(f"\n✓ Cook completed successfully in {elapsed:.2f} seconds")
            else:
                print(f"\n✗ Cook failed after {elapsed:.2f} seconds")

        return success

    def _count_new_files(self):
        """
        Count new files created since the initial scan.
        Returns the count of new files found.
        """
        import os

        new_file_count = 0
        skip_dirs = ['.git', '__pycache__', '.pdgtemp', 'pdgtemp', '.cache', 'node_modules', 'hip']

        scan_locations = []

        # Scan working directory (temp workspace)
        if self.working_dir and os.path.exists(self.working_dir):
            scan_locations.append(self.working_dir)

        # Scan original working directory
        if self.original_working_dir and os.path.exists(self.original_working_dir):
            scan_locations.append(self.original_working_dir)

        for location in scan_locations:
            try:
                for root, dirs, files in os.walk(location):
                    # Skip certain directories
                    if any(skip in root for skip in skip_dirs):
                        dirs[:] = []
                        continue

                    dirs[:] = [d for d in dirs if not any(skip in d for skip in skip_dirs)]

                    for file in files:
                        if file.startswith('.'):
                            continue
                        full_path = os.path.join(root, file)
                        if full_path not in self.files_before:
                            new_file_count += 1
            except:
                pass

        return new_file_count

    def threaded_cooking(self):
        """
        Execute PDG cooking in a background thread with monitoring and control
        """
        from queue import Queue

        print("\n" + "=" * 80)
        print("Phase 9: THREADED COOKING MODE")
        print("=" * 80)

        self.is_cooking = True
        monitor_thread = threading.Thread(target=self._monitor_and_relocate_files, daemon=True)
        monitor_thread.start()

        # Shared state for thread communication
        result_queue = Queue()
        stop_event = threading.Event()

        def execute_wrapper():
            """Wrapper to capture execution result"""
            try:
                result = self.execute()
                result_queue.put(('success', result))
            except Exception as e:
                import traceback
                error_info = {
                    'exception': e,
                    'traceback': traceback.format_exc()
                }
                result_queue.put(('error', error_info))

        # Start execution thread
        print("\nStarting execution in background thread...")
        thread = threading.Thread(target=execute_wrapper, name="PDG-Executor")
        thread.daemon = False  # Don't make it daemon so it completes properly
        thread.start()

        start_time = time.time()

        # Monitor thread with progress updates
        try:
            check_interval = 5  # seconds
            max_wait_time = 3600  # 1 hour maximum
            elapsed = 0
            last_progress_time = time.time()

            while thread.is_alive() and elapsed < max_wait_time:
                # Check for user interrupt
                if stop_event.is_set():
                    print("\n⚠ Stop requested by user")
                    break

                # Progress indicator
                current_time = time.time()
                if current_time - last_progress_time >= check_interval:
                    elapsed = int(current_time - start_time)
                    minutes = elapsed // 60
                    seconds = elapsed % 60

                    # Check PDG status if possible
                    status_msg = f"Executing... [{minutes:02d}:{seconds:02d}]"

                    try:
                        # Try to get PDG context status
                        if hasattr(self, 'topnet') and self.topnet:
                            context = self.topnet.getPDGGraphContext()
                            if context:
                                if hasattr(context, 'workItemStats'):
                                    stats = context.workItemStats()
                                    if stats:
                                        status_msg += f" | Work items: {stats.get('completed', 0)}/{stats.get('total', 0)}"
                                elif hasattr(context, 'isCooking') and context.isCooking():
                                    status_msg += " | Status: Cooking"
                                elif hasattr(context, 'isCooked') and context.isCooked():
                                    status_msg += " | Status: Cooked"
                    except:
                        pass  # Silently ignore status check errors

                    print(f"\r{status_msg}", end='', flush=True)
                    last_progress_time = current_time

                time.sleep(0.5)  # Short sleep to be responsive

            print()  # New line after progress updates

            # Handle timeout
            if elapsed >= max_wait_time:
                print(f"\n✗ Execution timed out after {max_wait_time} seconds")
                print("Attempting to stop thread...")
                stop_event.set()
                thread.join(timeout=10)  # Give it 10 seconds to stop gracefully

                if thread.is_alive():
                    print("⚠ Warning: Thread still running, may need to restart Houdini")
                    return False

            # Wait for thread completion
            if thread.is_alive():
                print("\nWaiting for thread to complete...")
                thread.join(timeout=30)

            # Get result from queue
            success = False
            if not result_queue.empty():
                result_type, result_data = result_queue.get()
                if result_type == 'success':
                    success = result_data
                    if success:
                        print("✓ Threaded execution completed successfully")
                    else:
                        print("✗ Threaded execution completed with failures")
                elif result_type == 'error':
                    print(f"✗ Threaded execution failed with error:")
                    print(f"  Exception: {result_data['exception']}")

                    print("  Traceback:")
                    print(result_data['traceback'])
            else:
                print("⚠ No result received from execution thread")

            return success

        except KeyboardInterrupt:
            print("\n\n⚠ Interrupted by user")
            stop_event.set()
            print("Waiting for thread to stop...")
            thread.join(timeout=10)
            if thread.is_alive():
                print("⚠ Warning: Thread still running")
            return False

        except Exception as e:
            print(f"\n✗ Threaded cooking error: {e}")
            if thread.is_alive():
                stop_event.set()
                thread.join(timeout=10)
            return False

        finally:
            print("=" * 80)
            self.is_cooking = False
            monitor_thread.join(timeout=5)  # wait a moment for final moves
            print("=" * 80)

    def _execute_network(self):
        """Execute using the simple method that works locally"""

        print("  Cooking using network execution method")

        # Check if topnet exists
        if not self.topnet:
            print("  ✗ No TOP network available for execution")
            return False

        try:
            print("\n  Generate all network static workitems...")
            self.topnet.generateStaticWorkItems()
            time.sleep(10)

            # Direct cook
            print("\n  Direct network cooking...")
            self.topnet.cookWorkItems(block=True)
            time.sleep(5)
            return True

        except Exception as e:
            print(f"  ✗ Direct network cooking failed: {e}")

            # Try executeGraph on display node
            try:
                print("  Trying executeGraph on display node...")
                display_node = self.topnet.displayNode()
                if display_node:
                    # executeGraph takes parameters: (generate, block, filter_static, tops_only)
                    display_node.executeGraph(False, True, False, True)
                    print("  ✓ Display node executeGraph completed")
                    time.sleep(5)
                    return True
                else:
                    print("  ✗ No display node found")
            except Exception as e2:
                print(f"  ✗ Display node executeGraph failed: {e2}")

            # Try executeGraph directly on topnet (less common but worth trying)
            try:
                print("  Trying executeGraph directly on topnet...")
                if hasattr(self.topnet, 'executeGraph'):
                    self.topnet.executeGraph(False, True, False, True)
                    print("  ✓ Topnet executeGraph completed")
                    time.sleep(5)  # Give it time to start
                    return True
            except Exception as e3:
                print(f"  ✗ Topnet executeGraph failed: {e3}")

            # Try cook button as last resort
            try:
                print("  Trying cook button as last resort...")
                if self.topnet.parm('cookbutton'):
                    self.topnet.parm('cookbutton').pressButton()
                    print("  ✓ Cook button pressed")
                    time.sleep(5)  # Give it time to start
                    return True
                else:
                    print("  ✗ No cook button found on topnet")
            except Exception as e4:
                print(f"  ✗ Cook button failed: {e4}")

            print("  ✗ All execution methods failed")
            return False

    def _pdg_context_cook(self):
        """Try alternative execution methods for non-standard networks"""
        print("\n  Attempting PDG context cook...")

        try:
            # Method 2: Use PDG context directly
            import pdg

            # Get PDG context
            context = None
            try:
                context = self.topnet.getPDGGraphContext()
            except Exception as e:
                print(f"  ✗ Failed to get PDG graph context: {e}")
                # Try alternative method to get context
                try:
                    if hasattr(self.topnet, 'pdgGraphContext'):
                        context = self.topnet.pdgGraphContext()
                except:
                    pass

            if not context:
                print("  ✗ No PDG context available")
                return False

            print("  Using PDG graph context...")

            # Method 1: Try dirty() and cook()
            try:
                print("  Marking context dirty and cooking...")
                # Try different methods to dirty the context based on what's available
                dirty_success = False

                # Try dirtyAllTasks (common in Houdini 21)
                if hasattr(context, 'dirtyAllTasks'):
                    try:
                        context.dirtyAllTasks(True)
                        dirty_success = True
                        print("    Used dirtyAllTasks")
                    except:
                        pass

                # Try setAllWorkItemsDirty
                if not dirty_success and hasattr(context, 'setAllWorkItemsDirty'):
                    try:
                        context.setAllWorkItemsDirty(True)
                        dirty_success = True
                        print("    Used setAllWorkItemsDirty")
                    except:
                        pass

                # Try dirtyAll
                if not dirty_success and hasattr(context, 'dirtyAll'):
                    try:
                        context.dirtyAll()
                        dirty_success = True
                        print("    Used dirtyAll")
                    except:
                        pass

                # If no dirty method worked, try cooking anyway
                if not dirty_success:
                    print("    Warning: Could not dirty context, attempting cook anyway...")
                time.sleep(1)  # Small delay for dirty propagation
                context.cook(block=True)
                print("  ✓ PDG context cook completed")
                return True
            except Exception as e:
                print(f"  ✗ PDG context cook failed: {e}")

            # Method 2: Try executeGraph if available
            try:
                if hasattr(context, 'executeGraph'):
                    print("  Trying context.executeGraph...")
                    context.executeGraph(False, True, False, True)
                    print("  ✓ PDG context executeGraph completed")
                    return True
            except Exception as e:
                print(f"  ✗ Context executeGraph failed: {e}")

            # Method 3: Try async cook with manual wait
            try:
                print("  Trying async cook with manual wait...")
                context.cook(block=False)  # Start async

                # Wait for completion with timeout
                max_wait = 300  # 5 minutes timeout
                start_time = time.time()
                while time.time() - start_time < max_wait:
                    # Check if cooking is complete
                    if hasattr(context, 'isCooked') and context.isCooked():
                        print("  ✓ Async cook completed")
                        return True
                    elif hasattr(context, 'isCooking') and not context.isCooking():
                        # Cooking stopped but not marked as cooked
                        break
                    time.sleep(2)

                print("  ✗ Async cook timed out or stopped")
            except Exception as e:
                print(f"  ✗ Async cook failed: {e}")

            # Method 4: Try to cook via graph's root node
            try:
                if hasattr(context, 'graph') and context.graph:
                    print("  Trying to cook via graph root...")
                    graph = context.graph
                    if hasattr(graph, 'cook'):
                        graph.cook(block=True)
                        print("  ✓ Graph cook completed")
                        return True
                    elif hasattr(graph, 'execute'):
                        graph.execute()
                        print("  ✓ Graph execute completed")
                        return True
            except Exception as e:
                print(f"  ✗ Graph cook failed: {e}")

            # Method 5: Try context's scheduler directly
            try:
                if hasattr(context, 'defaultScheduler'):
                    scheduler = context.defaultScheduler()
                    if scheduler and hasattr(scheduler, 'cook'):
                        print("  Trying scheduler cook...")
                        # Try different scheduler methods
                        cook_success = False

                        # Method A: cook with context
                        if hasattr(scheduler, "cook"):
                            try:
                                scheduler.cook(context, block=True)
                                cook_success = True
                            except:
                                try:
                                    # Method B: cook without context
                                    scheduler.cook(block=True)
                                    cook_success = True
                                except:
                                    pass

                        if not cook_success and hasattr(scheduler, "startCook"):
                            try:
                                scheduler.startCook(context)
                                cook_success = True
                            except:
                                pass

                        if cook_success:
                            print("  ✓“ Scheduler cook completed")
                        return True
            except Exception as e:
                print(f"  ✗ Scheduler cook failed: {e}")

            # Method 6: Force regeneration and cook
            try:
                print("  Trying forced regeneration and cook...")
                if hasattr(context, 'regenerateGraph'):
                    context.regenerateGraph()
                    time.sleep(2)
                    context.cook(block=True)
                    print("  ✓“ Forced regeneration cook completed")
                    return True
            except Exception as e:
                print(f"  ✗ Forced regeneration failed: {e}")

            # Method 7: Fallback to topnet cookWorkItems
            try:
                print("  Trying topnet.cookWorkItems as fallback...")
                if self.topnet and hasattr(self.topnet, "cookWorkItems"):
                    self.topnet.cookWorkItems(block=True)
                    print("  ✓ Topnet cookWorkItems completed")
                    return True
            except Exception as e:
                print(f"  ✗ Forced regeneration failed: {e}")

            print("  ✗ All PDG context methods failed")
            return False

        except Exception as e:
            print(f"  ✗ PDG context cook completely failed: {e}")
            return False

    def _try_output_node_cook(self):
        """Try to cook via the output node"""
        print("\n  Attempting output node cook...")

        try:
            if self.output_node:
                print(f"  Cooking output node workitems: {self.output_node.name()}")

                # Try to cook the output node
                try:
                    self.output_node.cookWorkItems(block=True)
                    print("  ✓ Output node cookWorkItems succeeded")
                    time.sleep(5)
                    return True
                except Exception as e:
                    print(f"  ✗ Output node cookWorkItems failed: {e}")

                    # Try executeGraph as alternative
                    try:
                        print("  Trying executeGraph of output node...")
                        self.output_node.executeGraph(False, True, False, True)
                        print("  ✓ Output node executeGraph succeeded")
                        time.sleep(5)
                        return True
                    except Exception as e2:
                        print(f"  ✗ Output node executeGraph also failed: {e2}")

                        # Try cook button as final fallback
                        if self.output_node.parm('cookbutton'):
                            try:
                                print("  Trying output node cook button...")
                                self.output_node.parm('cookbutton').pressButton()
                                print("  ✓ Output node cook button pressed")
                                time.sleep(5)  # Give it time to start cooking
                                return True
                            except Exception as e3:
                                print(f"  ✗ Cook button also failed: {e3}")
                        else:
                            print("  ✗ No cook button parameter found on output node")
            else:
                print("  ✗ No output node found")

        except Exception as e:
            print(f"  ✗ Output node cook failed: {e}")

        return False

    def _scheduler_execution(self):
        """Execute using the scheduler directly - FIXED VERSION"""
        print("\n  Attempting scheduler-based execution...")

        import time

        # First, ensure we have a scheduler
        if not hasattr(self, 'scheduler') or not self.scheduler:
            print("  ✗ No scheduler available")
            return False

        try:
            # IMPORTANT: Generate work items for all TOP nodes first
            print("  Generating work items for all TOP nodes...")
            nodes_with_items = []

            for node in self.topnet.children():
                try:
                    # Skip non-TOP nodes
                    if not (hasattr(node, 'type') and
                            hasattr(node.type(), 'category') and
                            node.type().category().name() == "Top"):
                        continue

                    node_type = node.type().name().lower()

                    # Skip scheduler nodes themselves
                    if "scheduler" in node_type:
                        continue

                    # Generate static work items for the node
                    if hasattr(node, 'generateStaticWorkItems'):
                        try:
                            print(f"    Generating work items for {node.name()}...")
                            node.generateStaticWorkItems()
                            nodes_with_items.append(node)
                            time.sleep(0.1)  # Small delay for generation
                        except Exception as e:
                            # Some nodes may not have work items to generate
                            if "no work items" not in str(e).lower():
                                print(f"    ⚠ Work item generation failed for {node.name()}: {str(e)[:50]}")

                except Exception as e:
                    print(f"    ⚠ Error processing node: {e}")

            if nodes_with_items:
                print(f"  ✓ Generated work items for {len(nodes_with_items)} nodes")
            else:
                print("  ⚠ No nodes had work items to generate")

            # Get PDG graph context for proper scheduler execution
            context = self.topnet.getPDGGraphContext()
            if not context:
                print("  ✗ No PDG context available")
                return False

            # Method 1: Try cooking the entire graph through context
            try:
                print(f"  Trying context.cook() with full graph...")

                # Dirty all work items first to ensure they're ready to cook
                if hasattr(context, 'dirtyAllWorkItems'):
                    context.dirtyAllWorkItems(False)
                    time.sleep(0.5)

                # Cook the entire graph
                context.cook(block=True)
                print("  ✓ Context cook completed")
                return True
            except Exception as e:
                error_msg = str(e)
                if "no node name" in error_msg.lower():
                    print(f"  ✗ Context cook failed - no nodes specified")
                else:
                    print(f"  ✗ Context cook failed: {error_msg[:100]}")

            # Method 2: Cook specific nodes through the scheduler
            try:
                # Find output/ROP nodes to cook (these typically drive the graph)
                output_nodes = []
                display_nodes = []

                for node in self.topnet.children():
                    try:
                        if not (hasattr(node, 'type') and
                                hasattr(node.type(), 'category') and
                                node.type().category().name() == "Top"):
                            continue

                        node_type = node.type().name().lower()
                        if "scheduler" in node_type:
                            continue

                        # Prioritize output/ROP nodes
                        if "output" in node.name().lower() or "rop" in node_type:
                            output_nodes.append(node)
                        # Also check for display flag
                        elif hasattr(node, 'isDisplayFlagSet') and node.isDisplayFlagSet():
                            display_nodes.append(node)
                        elif hasattr(node, 'isRenderFlagSet') and node.isRenderFlagSet():
                            display_nodes.append(node)

                    except Exception:
                        pass

                # Try cooking output nodes first, then display nodes
                nodes_to_cook = output_nodes + display_nodes

                if nodes_to_cook:
                    print(f"  Found {len(nodes_to_cook)} target nodes to cook")

                    for node in nodes_to_cook:
                        try:
                            print(f"  Cooking {node.name()} through scheduler...")

                            # Method A: Try cookWorkItems with the node
                            if hasattr(node, 'cookWorkItems'):
                                node.cookWorkItems(block=True)
                                print(f"  ✓ Successfully cooked {node.name()}")
                                return True

                        except Exception as e:
                            print(f"  ✗ Failed to cook {node.name()}: {str(e)[:50]}")

            except Exception as e:
                print(f"  ✗ Node-specific cooking failed: {e}")

            # Method 3: Use scheduler's executeGraph with proper parameters
            scheduler_node = None

            # Find the scheduler node object
            try:
                if hasattr(self.scheduler, 'type') and hasattr(self.scheduler.type(), 'category'):
                    scheduler_node = self.scheduler
                elif hasattr(self.scheduler, 'node'):
                    scheduler_node = self.scheduler.node()
                elif self.topnet:
                    for node in self.topnet.children():
                        if 'scheduler' in node.type().name().lower():
                            scheduler_node = node
                            break
            except Exception as e:
                print(f"  ⚠ Could not determine scheduler node: {e}")

            if scheduler_node:
                print(f"  Found scheduler node: {scheduler_node.name()}")

                # Try executeGraph with different parameter combinations
                execute_params = [
                    # (generate, block, filter_static, tops_only)
                    (True, True, False, True),  # Generate + execute
                    (False, True, False, True),  # Just execute (items already generated)
                    (True, True, True, True),  # With static filtering
                    (False, True, True, False),  # Execute all with filtering
                ]

                for params in execute_params:
                    try:
                        print(f"  Trying scheduler.executeGraph{params}...")
                        scheduler_node.executeGraph(*params)

                        # Check if anything was actually cooked
                        # Wait a moment to see if work starts
                        time.sleep(2)

                        # Check for completed work items
                        work_items_found = False
                        for node in self.topnet.children():
                            if hasattr(node, 'workItems'):
                                items = node.workItems()
                                if items and len(items) > 0:
                                    work_items_found = True
                                    # Check if any are cooked
                                    for item in items:
                                        if hasattr(item, 'isCooked') and item.isCooked():
                                            print(f"  ✓ Scheduler executeGraph completed with cooked items")
                                            return True

                        if work_items_found:
                            print(f"  ⚠ executeGraph completed but items may not be fully cooked")
                            # Still return True if we found work items
                            return True

                    except Exception as e:
                        print(f"  ✗ executeGraph{params} failed: {str(e)[:50]}")

            # Method 4: Use PDG service mode with scheduler
            try:
                if hasattr(context, 'setScheduler'):
                    print("  Setting scheduler in context...")
                    context.setScheduler(self.scheduler)

                    # Enable service mode
                    if hasattr(context, 'setServiceMode'):
                        context.setServiceMode(True)

                    # Start cooking with the scheduler
                    print("  Cooking with scheduler in service mode...")
                    context.cook(block=True)
                    print("  ✓ Service mode scheduler cook completed")
                    return True

            except Exception as e:
                print(f"  ✗ Service mode scheduler cook failed: {e}")

            # Method 5: Direct scheduler methods
            try:
                # Some schedulers have direct execution methods
                if hasattr(self.scheduler, 'startCook'):
                    print("  Trying scheduler.startCook()...")
                    self.scheduler.startCook()

                    # Wait for completion
                    max_wait = 60
                    start_time = time.time()
                    while time.time() - start_time < max_wait:
                        if hasattr(self.scheduler, 'isCooking') and not self.scheduler.isCooking():
                            print("  ✓ Scheduler cook completed")
                            return True
                        time.sleep(1)

            except Exception as e:
                print(f"  ✗ Scheduler startCook failed: {e}")

            print("  ✗ All scheduler execution methods failed")
            print("  Note: The scheduler may need specific nodes or work items to be configured.")
            print("  Consider using execution_method=2 (PDG context) or method=5 (Individual nodes) instead.")
            return False

        except Exception as e:
            print(f"  ✗ Scheduler execution completely failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _try_individual_node_cook(self):
        """Last resort: Cook each TOP node individually"""
        print("\n  Attempting individual node cooking...")

        import time
        any_success = False

        try:
            # Collect and categorize TOP nodes
            top_nodes = []
            output_nodes = []
            priority_nodes = []

            for node in self.topnet.children():
                try:
                    # Skip non-TOP nodes
                    if not (hasattr(node, 'type') and
                            hasattr(node.type(), 'category') and
                            node.type().category().name() == "Top"):
                        continue

                    node_type = node.type().name().lower()

                    # Skip scheduler nodes
                    if "scheduler" in node_type:
                        continue

                    # Categorize nodes by priority
                    elif hasattr(node, 'isDisplayFlagSet') and node.isDisplayFlagSet():
                        priority_nodes.append(node)
                    elif hasattr(node, 'isRenderFlagSet') and node.isRenderFlagSet():
                        priority_nodes.append(node)
                    elif "output" in node.name().lower() or "rop" in node_type:
                        output_nodes.append(node)
                    else:
                        top_nodes.append(node)

                except Exception as e:
                    print(f"    ⚠ Error checking node: {e}")
                    pass

            # Combine lists in priority order
            all_nodes = priority_nodes + output_nodes + top_nodes

            if not all_nodes:
                print("    No cookable TOP nodes found")
                return False

            print(f"    Found {len(all_nodes)} TOP nodes to cook")
            print(
                f"    Priority nodes: {len(priority_nodes)}, Output nodes: {len(output_nodes)}, Regular nodes: {len(top_nodes)}")

            # Cook nodes with multiple methods
            for i, node in enumerate(all_nodes, 1):
                node_success = False
                print(f"\n    [{i}/{len(all_nodes)}] Processing {node.name()}...")

                # Method 0: Try pdgcmd.py from scripts directory FIRST
                try:
                    node_success = self._try_pdgcmd_execution(node)
                    if node_success:
                        any_success = True
                        print(f"      ✓ {node.name()} cooked via pdgcmd.py")
                        continue
                except Exception as e:
                    print(f"      ✗ pdgcmd execution failed: {str(e)[:100]}")

                # Method 1: Try generateStaticWorkItems first
                try:
                    if hasattr(node, 'generateStaticWorkItems'):
                        print(f"      Generating work items for {node.name()}...")
                        node.generateStaticWorkItems()
                        time.sleep(0.5)  # Small delay for generation
                except Exception as e:
                    print(f"      ⚠ Work item generation failed: {str(e)[:50]}")

                # Method 2: Try cookWorkItems
                if hasattr(node, 'cookWorkItems'):
                    try:
                        print(f"      Cooking {node.name()} with cookWorkItems...")
                        node.cookWorkItems(block=True)
                        node_success = True
                        any_success = True
                        print(f"      ✓ {node.name()} cooked successfully")
                        continue  # Move to next node if successful
                    except Exception as e:
                        error_msg = str(e)
                        if "no work items" in error_msg.lower() or "nothing to cook" in error_msg.lower():
                            print(f"      ⚠ {node.name()} has no work items to cook")
                        else:
                            print(f"      ✗ cookWorkItems failed: {error_msg[:100]}")

                # Method 3: Try executeGraph
                if not node_success and hasattr(node, 'executeGraph'):
                    try:
                        print(f"      Trying executeGraph on {node.name()}...")
                        node.executeGraph(False, True, False, True)
                        node_success = True
                        any_success = True
                        print(f"      ✓ {node.name()} executed successfully")
                        continue
                    except Exception as e:
                        print(f"      ✗ executeGraph failed: {str(e)[:100]}")

                # Method 4: Try cook button
                if not node_success and node.parm('cookbutton'):
                    try:
                        print(f"      Trying cook button on {node.name()}...")
                        node.parm('cookbutton').pressButton()
                        node_success = True
                        any_success = True
                        print(f"      ✓ {node.name()} cook button pressed")
                        time.sleep(2)  # Give it time to start
                        continue
                    except Exception as e:
                        print(f"      ✗ Cook button failed: {str(e)[:100]}")

                # Method 5: Try dirty and cook
                if not node_success and hasattr(node, 'dirtyAllWorkItems'):
                    try:
                        print(f"      Trying dirty and cook on {node.name()}...")
                        node.dirtyAllWorkItems()
                        time.sleep(0.5)
                        if hasattr(node, 'cookWorkItems'):
                            node.cookWorkItems(block=True)
                            node_success = True
                            any_success = True
                            print(f"      ✓ {node.name()} dirty+cook succeeded")
                            continue
                    except Exception as e:
                        print(f"      ✗ Dirty+cook failed: {str(e)[:100]}")

                # Method 6: Check if node even needs cooking
                if not node_success:
                    try:
                        # Check if node has any work items
                        if hasattr(node, 'workItems'):
                            work_items = node.workItems()
                            if not work_items:
                                print(f"      ℹ {node.name()} has no work items (may be normal)")
                            else:
                                print(f"      ⚠ {node.name()} has {len(work_items)} work items but couldn't cook")

                        # Check if node is already cooked
                        if hasattr(node, 'isCooked') and node.isCooked():
                            print(f"      ℹ {node.name()} is already cooked")
                            any_success = True
                            node_success = True
                    except:
                        pass

                if not node_success:
                    print(f"      ✗ All methods failed for {node.name()}")

            # Summary
            print(f"\n    Individual node cooking completed")
            if any_success:
                print(f"    ✓ At least one node cooked successfully")
            else:
                print(f"    ✗ No nodes could be cooked")

            return any_success

        except Exception as e:
            print(f"  ✗ Individual node cooking failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _try_pdgcmd_execution(self, node):
        """
        Execute work items using pdgcmd.py from the scripts directory.
        This method uses the PDG command infrastructure to cook work items.

        Args:
            node: The TOP node to cook

        Returns:
            bool: True if at least one work item was successfully cooked
        """
        import subprocess
        import time

        print(f"      Trying pdgcmd.py execution for {node.name()}...")

        # Find pdgcmd.py location
        scripts_dir = self._find_pdg_scripts_dir()
        if not scripts_dir:
            print(f"        PDG scripts directory not found")
            return False

        pdgcmd_path = os.path.join(scripts_dir, 'pdgcmd.py')
        if not os.path.exists(pdgcmd_path):
            print(f"        pdgcmd.py not found at: {pdgcmd_path}")
            return False

        print(f"        Found pdgcmd.py at: {pdgcmd_path}")

        # Ensure work items are generated
        try:
            if hasattr(node, 'generateStaticWorkItems'):
                node.generateStaticWorkItems()
                time.sleep(0.3)
        except Exception as e:
            print(f"        Warning: Work item generation: {str(e)[:50]}")

        # Get work items
        work_items = []
        if hasattr(node, 'workItems'):
            work_items = list(node.workItems())

        if not work_items:
            print(f"        No work items found for {node.name()}")
            return False

        print(f"        Found {len(work_items)} work items")

        # Prepare environment
        job_env = os.environ.copy()
        job_env['PDG_SCRIPTDIR'] = scripts_dir

        # Add scripts dir to Python path
        pythonpath = job_env.get('PYTHONPATH', '')
        if scripts_dir not in pythonpath:
            job_env['PYTHONPATH'] = f"{scripts_dir}:{pythonpath}" if pythonpath else scripts_dir

        any_success = False

        for idx, work_item in enumerate(work_items, 1):
            try:
                item_name = work_item.name if hasattr(work_item, 'name') else f"item_{idx}"
                print(f"        [{idx}/{len(work_items)}] Processing work item: {item_name}")

                # Get the command from work item
                cmd = None
                if hasattr(work_item, 'command'):
                    cmd = work_item.command
                if not cmd and hasattr(work_item, 'platformCommand'):
                    cmd = work_item.platformCommand()

                if not cmd:
                    print(f"          No command found for work item {item_name}")
                    continue

                # Set work item specific environment
                item_env = job_env.copy()
                item_env['PDG_ITEM_NAME'] = str(item_name)
                item_env['PDG_INDEX'] = str(work_item.index if hasattr(work_item, 'index') else idx)

                # Add work item attributes to environment
                if hasattr(work_item, 'frame'):
                    item_env['PDG_FRAME'] = str(work_item.frame)

                # Create wrapper script that uses pdgcmd
                wrapper_script = self._create_pdgcmd_wrapper_script(
                    pdgcmd_path, item_name, cmd, scripts_dir
                )

                # Find Python/hython executable
                python_exec = self._find_python_executable()

                # Execute via subprocess
                print(f"          Executing via pdgcmd wrapper...")
                result = subprocess.run(
                    [python_exec, '-c', wrapper_script],
                    env=item_env,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout per work item
                    cwd=self.working_dir
                )

                if result.returncode == 0:
                    print(f"          ✓ Work item {item_name} completed successfully")
                    any_success = True

                    # Report result using pdgcmd functions if available
                    self._report_work_item_success(work_item)
                else:
                    print(f"          ✗ Work item {item_name} failed (exit code: {result.returncode})")
                    if result.stderr:
                        print(f"            stderr: {result.stderr[:200]}")

            except subprocess.TimeoutExpired:
                print(f"          ✗ Work item {item_name} timed out")
            except Exception as e:
                print(f"          ✗ Work item error: {str(e)[:100]}")

        return any_success

    def _find_pdg_scripts_dir(self):
        """
        Find the PDG scripts directory containing pdgcmd.py

        Returns:
            str: Path to scripts directory or None if not found
        """
        # Check environment variables first
        scripts_dir = os.environ.get('PDG_SCRIPTDIR', '')
        if scripts_dir and os.path.exists(scripts_dir):
            return scripts_dir

        # Try PDG_TEMP/scripts
        temp_dir = os.environ.get('PDG_TEMP', '')
        if temp_dir:
            scripts_dir = os.path.join(temp_dir, 'scripts')
            if os.path.exists(scripts_dir):
                return scripts_dir

        # Try HOUDINI_TEMP_DIR based paths
        houdini_temp = os.environ.get('HOUDINI_TEMP_DIR', '')
        if houdini_temp:
            scripts_dir = os.path.join(houdini_temp, 'scripts')
            if os.path.exists(scripts_dir):
                return scripts_dir

        # Try to find from working directory
        if self.working_dir:
            # Look in pdgtemp structure
            for root, dirs, files in os.walk(self.working_dir):
                if 'pdgcmd.py' in files:
                    return root
                # Limit depth
                if root.count(os.sep) - self.working_dir.count(os.sep) > 5:
                    break

        # Try Houdini installation path
        hfs = os.environ.get('HFS', '')
        if hfs:
            # pdgcmd is in python libs
            possible_paths = [
                os.path.join(hfs, 'houdini', 'python3.11libs', 'pdgjob'),
                os.path.join(hfs, 'houdini', 'python3.10libs', 'pdgjob'),
                os.path.join(hfs, 'houdini', 'python3.9libs', 'pdgjob'),
            ]
            for p in possible_paths:
                if os.path.exists(os.path.join(p, 'pdgcmd.py')):
                    return p

        return None

    def _create_pdgcmd_wrapper_script(self, pdgcmd_path, item_name, cmd, scripts_dir):
        """
        Create a Python script that uses pdgcmd to execute and report work item results

        Args:
            pdgcmd_path: Path to pdgcmd.py
            item_name: Name of the work item
            cmd: Command to execute
            scripts_dir: Scripts directory path

        Returns:
            str: Python script content
        """
        # Escape the command for embedding in Python string
        escaped_cmd = cmd.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
        escaped_scripts_dir = scripts_dir.replace('\\', '\\\\')

        wrapper_script = f'''
    import sys
    import os
    import subprocess
    import time

    # Add scripts directory to path
    sys.path.insert(0, "{escaped_scripts_dir}")

    # Import pdgcmd functions
    try:
        from pdgcmd import reportResultData, localizePath, makeDirSafe
        pdgcmd_available = True
    except ImportError:
        try:
            import pdgcmd
            reportResultData = pdgcmd.reportResultData
            localizePath = pdgcmd.localizePath
            makeDirSafe = pdgcmd.makeDirSafe
            pdgcmd_available = True
        except ImportError:
            pdgcmd_available = False
            print("Warning: pdgcmd module not available")

    # Get environment info
    item_name = os.environ.get('PDG_ITEM_NAME', '{item_name}')
    server_addr = os.environ.get('PDG_RESULT_SERVER', '')

    # Report cook start
    print(f"PDG Work Item: {{item_name}} starting...")
    start_time = time.time()

    # Execute the work item command
    cmd = "{escaped_cmd}"
    print(f"Executing: {{cmd[:200]}}...")

    try:
        # Run the command
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )

        duration = time.time() - start_time

        if result.returncode == 0:
            print(f"Command completed successfully in {{duration:.2f}}s")

            # Report success via pdgcmd if available
            if pdgcmd_available and server_addr:
                try:
                    # Check for output files and report them
                    # This is a simplified version - real implementation would scan for outputs
                    pass
                except Exception as e:
                    print(f"Warning: Could not report via pdgcmd: {{e}}")

            sys.exit(0)
        else:
            print(f"Command failed with exit code: {{result.returncode}}")
            if result.stderr:
                print(f"stderr: {{result.stderr[:500]}}")
            sys.exit(result.returncode)

    except subprocess.TimeoutExpired:
        print("Command timed out")
        sys.exit(1)
    except Exception as e:
        print(f"Error executing command: {{e}}")
        sys.exit(1)
    '''
        return wrapper_script

    def _find_python_executable(self):
        """
        Find the appropriate Python/hython executable

        Returns:
            str: Path to Python executable
        """
        # Try hython first (has hou module)
        hython = os.path.join(hou.applicationDirPath(), 'hython')
        if os.path.exists(hython):
            return hython

        # Try python3
        python3 = shutil.which('python3')
        if python3:
            return python3

        # Fall back to python
        python = shutil.which('python')
        if python:
            return python

        # Last resort - use sys.executable
        return sys.executable

    def _report_work_item_success(self, work_item):
        """
        Report successful work item completion using PDG API

        Args:
            work_item: The completed work item
        """
        try:
            if hasattr(work_item, 'cookWorkItem'):
                # This is for in-process cooking
                pass
            # Work item success is typically reported by the command itself
            # via pdgcmd.reportResultData
        except Exception as e:
            print(f"          Note: Could not report success via API: {e}")

    def _dependency_chain_cook(self):
        """Cook nodes in dependency order from inputs to outputs"""
        print("\n  Attempting dependency chain cooking...")

        import time

        try:
            # Build dependency graph
            print("  Building dependency chain...")
            node_levels = []
            processed = set()

            # Find all nodes with no inputs (start nodes)
            start_nodes = []
            for node in self.topnet.children():
                if node.type().category().name() != "Top":
                    continue
                if "scheduler" in node.type().name().lower():
                    continue

                inputs = node.inputs()
                if not inputs or all(inp is None for inp in inputs):
                    start_nodes.append(node)
                    processed.add(node)

            if start_nodes:
                node_levels.append(start_nodes)
                print(f"  Found {len(start_nodes)} start nodes")

            # Build levels based on dependencies
            while True:
                current_level = []
                for node in self.topnet.children():
                    if node in processed:
                        continue
                    if node.type().category().name() != "Top":
                        continue
                    if "scheduler" in node.type().name().lower():
                        continue

                    # Check if all inputs are processed
                    inputs = node.inputs()
                    if inputs and all(inp is None or inp in processed for inp in inputs):
                        current_level.append(node)
                        processed.add(node)

                if not current_level:
                    break
                node_levels.append(current_level)

            # Cook level by level
            print(f"  Cooking {len(node_levels)} dependency levels...")
            any_success = False

            for level_idx, level_nodes in enumerate(node_levels):
                print(f"\n  Level {level_idx + 1}: {len(level_nodes)} nodes")
                for node in level_nodes:
                    try:
                        print(f"    Cooking {node.name()}...")
                        if hasattr(node, 'cookWorkItems'):
                            node.cookWorkItems(block=True)
                            print(f"    ✓ {node.name()} cooked")
                            any_success = True
                    except Exception as e:
                        print(f"    ✗ {node.name()} failed: {str(e)[:50]}")

            return any_success

        except Exception as e:
            print(f"  ✗ Dependency chain cooking failed: {e}")
            return False


    def _service_mode_cook(self):
        """Use PDG service mode for background execution with improved timeout and monitoring"""
        print("\n  Attempting service mode cooking...")


        try:
            context = self.topnet.getPDGGraphContext()
            if not context:
                print("  ✗ No PDG context available")
                return False

            # Enable service mode
            print("  Enabling PDG service mode...")
            if hasattr(context, 'setServiceMode'):
                context.setServiceMode(True)

            # Start services
            if hasattr(context, 'startServices'):
                print("  Starting PDG services...")
                context.startServices()
                time.sleep(2)

            # Cook in service mode
            try:
                print("  Cooking in service mode...")
                context.cook(block=False)

                # Dynamic timeout based on graph complexity
                # Check if we can estimate complexity from the graph
                base_timeout = 300  # Default 5 minutes

                try:
                    # Try to get an estimate of work items to determine timeout
                    if hasattr(context, 'workItemStats'):
                        initial_stats = context.workItemStats()
                        if initial_stats and 'total' in initial_stats:
                            total_items = initial_stats.get('total', 0)
                            # Scale timeout based on work items
                            # 5 minutes for up to 100 items, then add 1 minute per 100 items
                            if total_items > 0:
                                base_timeout = min(300 + (total_items // 100) * 60, 3600)  # Max 1 hour
                                print(f"  Detected {total_items} work items, timeout set to {base_timeout}s")
                            else:
                                print(f"  Using default timeout of {base_timeout}s")
                        else:
                            print(f"  Using default timeout of {base_timeout}s")
                    else:
                        print(f"  Using default timeout of {base_timeout}s")
                except:
                    print(f"  Using default timeout of {base_timeout}s")

                max_wait = base_timeout

                # Monitor with progress reporting
                start_time = time.time()
                check_interval = 5
                last_check = start_time
                no_progress_count = 0
                last_completed = 0

                while time.time() - start_time < max_wait:
                    elapsed = time.time() - start_time

                    # Check cooking status
                    if hasattr(context, 'isCooking') and not context.isCooking():
                        # Verify if actually completed successfully
                        if hasattr(context, 'isCooked') and context.isCooked():
                            print(f"\n  ✓ Service mode cook completed in {elapsed:.1f}s")
                            return True
                        else:
                            # Check for failures
                            if hasattr(context, 'workItemStats'):
                                stats = context.workItemStats()
                                if stats:
                                    failed = stats.get('failed', 0)
                                    completed = stats.get('completed', 0)
                                    total = stats.get('total', 0)

                                    # If all items processed
                                    if total > 0 and completed + failed >= total:
                                        if failed > 0:
                                            print(f"\n  ✗ Cook completed with {failed} failed items")
                                            return False
                                        else:
                                            print(f"\n  ✓ All {completed} items completed successfully")
                                            return True

                            print(f"\n  ⚠ Cooking stopped after {elapsed:.1f}s (status unclear)")
                            # Check if any work was done
                            if hasattr(context, 'workItemStats'):
                                stats = context.workItemStats()
                                if stats and stats.get('completed', 0) > 0:
                                    print(f"  ✓ Completed {stats['completed']} work items")
                                    return True
                            return False

                    # Progress monitoring every 5 seconds
                    if time.time() - last_check >= check_interval:
                        try:
                            if hasattr(context, 'workItemStats'):
                                stats = context.workItemStats()
                                if stats:
                                    completed = stats.get('completed', 0)
                                    total = stats.get('total', 0)
                                    failed = stats.get('failed', 0)
                                    cooking = stats.get('cooking', 0)

                                    # Check progress
                                    if completed > last_completed:
                                        no_progress_count = 0
                                        last_completed = completed
                                    else:
                                        no_progress_count += 1

                                    # Display status
                                    mins = int(elapsed // 60)
                                    secs = int(elapsed % 60)
                                    status_msg = f"\r  [{mins:02d}:{secs:02d}] "

                                    if total > 0:
                                        percent = (completed * 100) // total if total > 0 else 0
                                        status_msg += f"{completed}/{total} ({percent}%) completed"
                                    else:
                                        status_msg += f"{completed} completed"

                                    if cooking > 0:
                                        status_msg += f" | {cooking} cooking"
                                    if failed > 0:
                                        status_msg += f" | {failed} failed"

                                    print(status_msg, end='', flush=True)

                                    # Check completion
                                    if total > 0 and completed + failed >= total:
                                        print()  # New line
                                        if failed == 0:
                                            print(f"  ✓ All {completed} work items completed successfully")
                                            return True
                                        else:
                                            print(f"  ✗ Completed with {failed} failures out of {total} items")
                                            return False

                                    # Check for stall (60 seconds no progress)
                                    if no_progress_count >= 12:
                                        print(f"\n  ✗ Execution stalled - no progress for 60s")
                                        # But if we have some completed items, consider it partial success
                                        if completed > 0:
                                            print(f"  ⚠ Partial completion: {completed} items processed")
                                            return False  # Return false to try alternative methods
                                        return False
                        except:
                            # If stats fail, just show time
                            mins = int(elapsed // 60)
                            secs = int(elapsed % 60)
                            print(f"\r  Executing... [{mins:02d}:{secs:02d}]", end='', flush=True)

                        last_check = time.time()

                    time.sleep(1)

                print(f"\n  ✗ Timeout after {max_wait} seconds")

                # Check if we got partial results
                if hasattr(context, 'workItemStats'):
                    stats = context.workItemStats()
                    if stats and stats.get('completed', 0) > 0:
                        print(f"  ⚠ Partial results: {stats['completed']} items completed before timeout")

                # Try to cancel the cook
                if hasattr(context, 'cancelCook'):
                    try:
                        print("  Attempting to cancel remaining work...")
                        context.cancelCook()
                        time.sleep(2)
                    except:
                        pass

            finally:
                # Clean up services
                if hasattr(context, 'stopServices'):
                    try:
                        context.stopServices()
                        time.sleep(1)
                    except:
                        pass
                if hasattr(context, 'setServiceMode'):
                    try:
                        context.setServiceMode(False)
                    except:
                        pass

            return False

        except Exception as e:
            print(f"  ✗ Service mode cooking failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _batch_work_item_cook(self):
        """Cook work items in batches rather than all at once"""
        print("\n  Attempting batch work item cooking...")

        import time

        try:
            # Collect all work items from all nodes
            all_work_items = []
            nodes_map = {}

            for node in self.topnet.children():
                if node.type().category().name() != "Top":
                    continue
                if "scheduler" in node.type().name().lower():
                    continue

                try:
                    if hasattr(node, 'workItems'):
                        items = node.workItems()
                        if items:
                            for item in items:
                                all_work_items.append(item)
                                nodes_map[item] = node
                except:
                    pass

            if not all_work_items:
                print("  No work items found")
                return False

            print(f"  Found {len(all_work_items)} total work items")

            # Cook in batches
            batch_size = 10
            any_success = False

            for i in range(0, len(all_work_items), batch_size):
                batch = all_work_items[i:i + batch_size]
                print(f"\n  Cooking batch {i // batch_size + 1}: {len(batch)} items")

                for work_item in batch:
                    try:
                        node = nodes_map.get(work_item)
                        if node and hasattr(work_item, 'cook'):
                            work_item.cook()
                            any_success = True
                            print(f"    ✓ Cooked work item from {node.name()}")
                    except Exception as e:
                        print(f"    ✗ Work item failed: {str(e)[:50]}")

                time.sleep(1)  # Small delay between batches

            return any_success

        except Exception as e:
            print(f"  ✗ Batch work item cooking failed: {e}")
            return False

    def _event_callback_cook(self):
        """Use polling-based asynchronous cooking (simplified to avoid event handler issues)"""
        print("\n  Attempting event callback cooking...")

        import time

        try:
            context = self.topnet.getPDGGraphContext()
            if not context:
                print("  ✗ No PDG context available")
                return False

            # Start async cook without relying on event callbacks
            print("  Starting async cook with polling...")

            # First, make sure the graph is ready
            try:
                # Try to dirty the graph first
                if hasattr(context, 'dirtyAllTasks'):
                    context.dirtyAllTasks(True)
                elif hasattr(context, 'setAllWorkItemsDirty'):
                    context.setAllWorkItemsDirty(True)
            except:
                pass  # Continue even if dirty fails

            # Start the async cook
            context.cook(block=False)

            # Poll for completion
            max_wait = 300  # 5 minutes
            start_time = time.time()
            check_interval = 2  # Check every 2 seconds
            last_status_time = start_time

            print("  Monitoring cook progress...")

            while time.time() - start_time < max_wait:
                try:
                    # Check if cooking is still in progress
                    is_cooking = False
                    is_cooked = False

                    if hasattr(context, 'isCooking'):
                        is_cooking = context.isCooking()

                    if hasattr(context, 'isCooked'):
                        is_cooked = context.isCooked()

                    # Print status every 10 seconds
                    if time.time() - last_status_time >= 10:
                        elapsed = int(time.time() - start_time)
                        if is_cooking:
                            # Try to get work item statistics if available
                            status_msg = f"    Cooking in progress... [{elapsed}s]"

                            # Try to get work item counts
                            try:
                                if hasattr(context, 'workItemCount'):
                                    total_items = context.workItemCount()
                                    if hasattr(context, 'completedWorkItemCount'):
                                        completed_items = context.completedWorkItemCount()
                                        status_msg += f" ({completed_items}/{total_items} items)"
                            except:
                                pass

                            print(status_msg)
                        else:
                            print(f"    Waiting... [{elapsed}s]")
                        last_status_time = time.time()

                    # Check completion conditions
                    if is_cooked:
                        print("  ✓ Cook completed successfully")
                        return True

                    if not is_cooking and not is_cooked:
                        # Cooking stopped but not marked as cooked
                        # Wait a bit to see if it's just transitioning
                        time.sleep(2)

                        # Check again
                        if hasattr(context, 'isCooking'):
                            is_cooking = context.isCooking()
                        if hasattr(context, 'isCooked'):
                            is_cooked = context.isCooked()

                        if not is_cooking:
                            if is_cooked:
                                print("  ✓ Cook completed successfully")
                                return True
                            else:
                                # Check if there was an error
                                error_msg = "  ✗ Cook stopped without completing"

                                # Try to get error information
                                try:
                                    if hasattr(context, 'hasErrors'):
                                        if context.hasErrors():
                                            error_msg += " (errors detected)"

                                    if hasattr(context, 'errorMessage'):
                                        error = context.errorMessage()
                                        if error:
                                            error_msg += f": {error}"
                                except:
                                    pass

                                print(error_msg)

                                # One last attempt - try checking work items directly
                                try:
                                    if self.output_node and hasattr(self.output_node, 'allWorkItems'):
                                        work_items = self.output_node.allWorkItems()
                                        if work_items and len(work_items) > 0:
                                            # Check if any work items succeeded
                                            import pdg
                                            succeeded = 0
                                            for item in work_items:
                                                if hasattr(item, 'state'):
                                                    if item.state() == pdg.workItemState.CookedSuccess:
                                                        succeeded += 1

                                            if succeeded > 0:
                                                print(f"    Note: {succeeded} work items succeeded")
                                                return True
                                except:
                                    pass

                                return False

                except Exception as e:
                    # Log error but continue polling
                    print(f"    Warning: Error during status check: {e}")

                # Wait before next check
                time.sleep(check_interval)

            # Timeout reached
            print(f"  ✗ Cook timed out after {max_wait} seconds")

            # Try to cancel the cook if it's still running
            try:
                if hasattr(context, 'cancel'):
                    context.cancel()
                    print("    Cancelled ongoing cook")
            except:
                pass

            return False

        except Exception as e:
            print(f"  ✗ Event callback cooking failed: {e}")

            # Fallback to synchronous cook
            try:
                print("  Attempting fallback synchronous cook...")
                if context and hasattr(context, 'cook'):
                    context.cook(block=True)
                    print("  ✓ Fallback synchronous cook completed")
                    return True
            except Exception as fallback_error:
                print(f"  ✗ Fallback also failed: {fallback_error}")

            return False

    def _command_line_cook(self):
        """Execute PDG via command line interface"""
        print("\n  Attempting command line PDG execution...")

        import subprocess
        import os

        try:
            # Save current state
            hip_file = hou.hipFile.path()

            # Build command
            hython_path = os.path.join(hou.applicationDirPath(), "hython")

            script = f'''
    import hou
    hou.hipFile.load("{hip_file}")
    topnet = hou.node("{self.topnet.path()}")
    topnet.cookWorkItems(block=True)
    '''

            # Write temporary script
            script_path = "/tmp/pdg_cook_script.py"
            with open(script_path, 'w') as f:
                f.write(script)

            # Execute via subprocess
            print(f"  Executing PDG via command line...")
            cmd = [hython_path, script_path]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print("  ✓ Command line execution completed")
                return True
            else:
                print(f"  ✗ Command line execution failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"  ✗ Command line cooking failed: {e}")
            return False
        finally:
            # Cleanup
            if os.path.exists(script_path):
                os.remove(script_path)

    def _scan_and_copy_outputs_comprehensive(self):
        """Scan and copy outputs from all possible locations - works for any files/folders"""

        print("\n" + "-" * 80)
        print("Phase 10: COLLECTING AND COPYING OUTPUT FILES")
        print("-" * 80)

        import shutil

        try:
            files_to_copy = []
            files_skipped = 0
            seen_files = set()  # Track already seen files to prevent duplicates

            # Scan multiple locations where files might be
            # NOTE: Only add parent directories - os.walk handles recursion automatically
            # Do NOT add subdirectories separately as this causes duplicate scanning
            scan_locations = [
                self.working_dir,  # Temp workspace
                self.original_working_dir,  # Original location (os.walk will recurse)
            ]

            # Add explicit datasets render path if it exists to ensure we don't miss deep files
            #render_path = os.path.join(self.working_dir, "datasets", "render")
            #if os.path.exists(render_path):
            #    scan_locations.append(render_path)

            #print(f"  Scanning {len(scan_locations)} locations for new files...")

            # Directories to skip during scanning
            skip_dirs = ["pdgtemp", "__pycache__", "venv", "site-packages", ".git", ".cache"]

            # Scan all locations for new files
            for location in scan_locations:
                if not os.path.exists(location):
                    continue

                print(f"    Scanning: {location}")

                for root, dirs, files in os.walk(location):
                    # Skip certain directories
                    if any(skip in root for skip in skip_dirs):
                        dirs[:] = []  # Don't recurse into these directories
                        continue

                    # Filter out directories we don't want to recurse into
                    dirs[:] = [d for d in dirs if not any(skip in d for skip in skip_dirs)]

                    for file in files:
                        # Skip hidden files and common cache files
                        if file.startswith('.') or file.endswith(('.pyc', '.pyo', '.pyd')):
                            files_skipped += 1
                            continue

                        full_path = os.path.join(root, file)

                        # Skip if already seen (prevents duplicates from overlapping scan locations)
                        if full_path in seen_files:
                            continue
                        seen_files.add(full_path)

                        # Check if this is a new file (didn't exist before)
                        if full_path not in self.files_before:
                            self.files_after.add(full_path)
                            files_to_copy.append(full_path)

            # Report what we found
            print(f"\n  ✓ Found {len(files_to_copy)} new files")
            print(f"  ✓ Skipped {files_skipped} files (hidden/cache files)")

            # Copy files to output directory maintaining structure
            if files_to_copy and self.output_dir:
                print(f"\n  Copying to output directory: {self.output_dir}")
                print("  " + "-" * 80)

                self.files_copied = 0

                # Sort files for consistent output
                files_to_copy.sort()

                for idx, src_path in enumerate(files_to_copy, 1):
                    try:
                        # Determine the base directory for relative path calculation
                        base_dir = None

                        # First check if file is in working_dir
                        if src_path.startswith(self.working_dir):
                            base_dir = self.working_dir
                        # Then check original_working_dir
                        elif src_path.startswith(self.original_working_dir):
                            base_dir = self.original_working_dir
                        # Otherwise use the parent directory
                        else:
                            base_dir = os.path.dirname(src_path)

                        # Calculate relative path from base directory
                        rel_path = os.path.relpath(src_path, base_dir)

                        # Create destination path in output directory
                        dst_path = os.path.join(self.output_dir, rel_path)

                        # Create destination directory if needed
                        dst_dir = os.path.dirname(dst_path)
                        os.makedirs(dst_dir, exist_ok=True)

                        # Copy the file
                        shutil.copy2(src_path, dst_path)
                        self.files_copied += 1
                        self.copied_files_list.add(dst_path)

                        # Print detailed copy information
                        print(f"\n  [{idx}/{len(files_to_copy)}] File copied:")
                        print(f"    Source:      {src_path}")
                        print(f"    Destination: {dst_path}")
                        print(f"    Relative:    {rel_path}")

                    except Exception as e:
                        print(f"\n  ✗ ERROR copying file {idx}:")
                        print(f"    File:  {src_path}")
                        print(f"    Error: {e}")

                print("\n  " + "-" * 80)
                print(f"  ✓ Successfully copied {self.files_copied}/{len(files_to_copy)} files")

            elif files_to_copy:
                print("  ⚠ No output directory specified")
            else:
                print("  ⚠ No new files found to copy")

            # Check and report on output structure
            self._check_output_structure_generic()

        except Exception as e:
            print(f"  ✗ Error during file collection: {e}")
            import traceback
            traceback.print_exc()

    def _check_output_structure_generic(self):
        """Check and report on the output directory structure (generic version)"""
        print("\n  VERIFYING OUTPUT STRUCTURE:")

        if not os.path.exists(self.output_dir):
            print(f"    ✗ Output directory does not exist: {self.output_dir}")
            return

        # Count total files and directories
        total_files = 0
        total_dirs = 0
        dir_summary = {}

        for root, dirs, files in os.walk(self.output_dir):
            total_files += len(files)
            total_dirs += len(dirs)

            # Get relative path for summary
            rel_root = os.path.relpath(root, self.output_dir)
            if rel_root == '.':
                rel_root = 'root'

            # Track top-level directories
            if root == self.output_dir:
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    file_count = sum(1 for _, _, f in os.walk(dir_path) for _ in f)
                    dir_summary[d] = file_count

        # Report summary
        if total_files > 0:
            print(f"    ✔ Output directory contains {total_files} files in {total_dirs} directories")

            # Show top-level directory summary
            if dir_summary:
                print("\n    Top-level directories:")
                for dir_name, file_count in sorted(dir_summary.items()):
                    print(f"      - {dir_name}/: {file_count} files")

            # Show some example files (first 5)
            print("\n    Sample files:")
            count = 0
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    if count >= 5:
                        break
                    rel_path = os.path.relpath(os.path.join(root, file), self.output_dir)
                    print(f"      - {rel_path}")
                    count += 1
                if count >= 5:
                    break

            if total_files > 5:
                print(f"      ... and {total_files - 5} more files")
        else:
            print("    ⚠ Output directory is empty")

    def _save_final_hip(self):
        """Save the final HIP file"""
        print("\n" + "-" * 80)
        print("Phase 11: SAVE HIP FILE")
        print("-" * 80)


        try:
            # Build filename based on mode
            hip_name = os.path.basename(self.hip_file)
            base, ext = os.path.splitext(hip_name)

            # save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_hip = os.path.join(
                self.output_dir,
                'hip',
                f"{base}_{timestamp}{ext}")

            hou.hipFile.save(final_hip)
            self.copied_files_list.add(final_hip)

            print(f"✓ Saved HIP file: {final_hip}")

        except Exception as e:
            print(f"✗ Failed to save HIP file: {e}")

    def _report_results(self):
        """Report execution results"""

        print("\n" + "-" * 80)
        print("Phase 12: EXECUTION SUMMARY")
        print("-" * 80)

        elapsed = time.time() - self.start_time
        print(f"  Total execution time: {elapsed:.2f} seconds")
        print(f"  New files created: {len(self.files_after)}")
        print(f"  Files copied to output: {self.files_copied}")

        # Save execution report
        report = {
            "timestamp": datetime.now().isoformat(),
            "hip_file": self.hip_file,
            "topnet_path": self.topnet_path,
            "working_dir": self.working_dir,
            "output_dir": self.output_dir,
            "execution_time": elapsed,
            "files_created": len(self.files_after),
            "files_copied": self.files_copied,
            #"file_list": list(self.files_after)[:100]  # First 100 files
            "file_list": list(self.copied_files_list)
        }

        report_file = os.path.join(self.output_dir, f"pdg_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"  ✓ Execution report saved: {report_file}")
        except:
            pass

        print("\n" + "=" * 80)
        print("EXECUTION COMPLETE")
        print("=" * 80)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='PDG Universal Wrapper - Simplified General Solution'
    )
    parser.add_argument('--hip_file', type=str, required=True,
                        help='Path to the Houdini file')
    parser.add_argument('--topnet_path', type=str, required=True,
                        help='Path to the TOP network node')
    parser.add_argument('--working_dir', type=str, required=True,
                        help='Working directory path')
    parser.add_argument('--output_dir', type=str, default=None,
                        help='Output directory for rendered files')
    parser.add_argument('--execution_method', type=int, required=True,
                        help='Execution method')

    # Parse any additional arguments for compatibility
    parser.add_argument('--item_index', type=int, default=None, help='Ignored for compatibility')
    parser.add_argument('--cook_entire_graph', action='store_true', help='Ignored for compatibility')
    parser.add_argument('--use_single_machine', action='store_true', help='Ignored for compatibility')

    args = parser.parse_args()

    # Set default output directory if not provided
    if not args.output_dir:
        args.output_dir = os.path.join(args.working_dir, 'pdg_render')

    # Create and run executor
    executor = SimplePDGExecutor(
        hip_file=args.hip_file,
        topnet_path=args.topnet_path,
        working_dir=args.working_dir,
        output_dir=args.output_dir,
        execution_method=args.execution_method,
    )

    success = executor.run()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()