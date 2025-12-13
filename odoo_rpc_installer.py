#!/usr/bin/env python3
"""
Odoo RPC Installer for Property Fielder Addons
Installs and tests addons via Odoo XML-RPC API
"""

import xmlrpc.client
import time
import sys
from typing import Dict, List, Optional

class OdooRPCClient:
    """Client for interacting with Odoo via XML-RPC"""
    
    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
    def authenticate(self) -> bool:
        """Authenticate with Odoo"""
        try:
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            if self.uid:
                print(f"✅ Authenticated as user ID: {self.uid}")
                return True
            else:
                print("❌ Authentication failed")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def execute(self, model: str, method: str, *args, **kwargs):
        """Execute a method on an Odoo model"""
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )
    
    def search_read(self, model: str, domain: List, fields: List) -> List[Dict]:
        """Search and read records"""
        # In Odoo 19, search_read expects fields as a positional argument
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'search_read', [domain], {'fields': fields}
        )
    
    def update_module_list(self) -> bool:
        """Update the list of available modules"""
        try:
            print("\n📋 Updating module list...")
            # In Odoo 19, update_list() takes no arguments
            self.models.execute_kw(
                self.db, self.uid, self.password,
                'ir.module.module', 'update_list', []
            )
            print("✅ Module list updated")
            return True
        except Exception as e:
            print(f"❌ Error updating module list: {e}")
            return False
    
    def get_module_info(self, module_name: str) -> Optional[Dict]:
        """Get information about a module"""
        try:
            modules = self.search_read(
                'ir.module.module',
                [('name', '=', module_name)],
                ['name', 'state', 'summary', 'author', 'installed_version']
            )
            return modules[0] if modules else None
        except Exception as e:
            print(f"❌ Error getting module info: {e}")
            return None
    
    def install_module(self, module_name: str) -> bool:
        """Install a module"""
        try:
            print(f"\n🔧 Installing module: {module_name}")
            
            # Get module
            module = self.get_module_info(module_name)
            if not module:
                print(f"❌ Module '{module_name}' not found")
                return False
            
            # Check if already installed
            if module['state'] == 'installed':
                print(f"✅ Module '{module_name}' is already installed")
                return True
            
            # Install module
            module_id = module['id']
            self.execute('ir.module.module', 'button_immediate_install', [module_id])
            
            # Wait for installation
            print("⏳ Installing... (this may take a minute)")
            time.sleep(5)
            
            # Verify installation
            module = self.get_module_info(module_name)
            if module and module['state'] == 'installed':
                print(f"✅ Module '{module_name}' installed successfully!")
                print(f"   Version: {module.get('installed_version', 'N/A')}")
                print(f"   Author: {module.get('author', 'N/A')}")
                return True
            else:
                print(f"❌ Module '{module_name}' installation failed")
                print(f"   State: {module['state'] if module else 'Unknown'}")
                return False
                
        except Exception as e:
            print(f"❌ Error installing module '{module_name}': {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_module(self, module_name: str, tests: Dict) -> Dict:
        """Run tests on an installed module"""
        results = {
            'module': module_name,
            'tests_passed': 0,
            'tests_failed': 0,
            'details': []
        }
        
        print(f"\n🧪 Testing module: {module_name}")
        
        for test_name, test_config in tests.items():
            try:
                model = test_config['model']
                action = test_config.get('action', 'search')
                
                if action == 'search':
                    # Test if model exists and is accessible
                    count = self.execute(model, 'search_count', [[]])
                    print(f"  ✅ {test_name}: Found {count} records in {model}")
                    results['tests_passed'] += 1
                    results['details'].append({
                        'test': test_name,
                        'status': 'PASS',
                        'message': f'Model {model} accessible, {count} records'
                    })
                elif action == 'create':
                    # Test creating a record
                    values = test_config.get('values', {})
                    record_id = self.execute(model, 'create', [values])
                    print(f"  ✅ {test_name}: Created record ID {record_id}")
                    results['tests_passed'] += 1
                    results['details'].append({
                        'test': test_name,
                        'status': 'PASS',
                        'message': f'Created record ID {record_id}'
                    })
                    
            except Exception as e:
                print(f"  ❌ {test_name}: {e}")
                results['tests_failed'] += 1
                results['details'].append({
                    'test': test_name,
                    'status': 'FAIL',
                    'message': str(e)
                })
        
        return results


def main():
    """Main installation and testing workflow"""
    
    # Configuration
    ODOO_URL = "http://localhost:8069"
    ODOO_DB = "property_fielder"
    ODOO_USER = "admin"
    ODOO_PASSWORD = input("Enter Odoo admin password: ")
    
    print("=" * 60)
    print("Property Fielder Addon Installer")
    print("=" * 60)
    
    # Connect to Odoo
    client = OdooRPCClient(ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD)
    
    if not client.authenticate():
        print("\n❌ Failed to authenticate. Please check your credentials.")
        sys.exit(1)
    
    # Update module list
    if not client.update_module_list():
        print("\n❌ Failed to update module list")
        sys.exit(1)
    
    # Modules to install (in order)
    modules = [
        'property_fielder_field_service',
        'property_fielder_property_management',
        'property_fielder_field_service_mobile'
    ]
    
    # Install each module
    installation_results = []
    for module in modules:
        success = client.install_module(module)
        installation_results.append({
            'module': module,
            'installed': success
        })
        
        if not success:
            print(f"\n⚠️  Installation failed for {module}, continuing with next module...")
    
    print("\n" + "=" * 60)
    print("Installation Summary")
    print("=" * 60)
    
    for result in installation_results:
        status = "✅ INSTALLED" if result['installed'] else "❌ FAILED"
        print(f"{status}: {result['module']}")
    
    print("\n✨ Installation process complete!")
    print(f"\n🌐 Access Odoo at: {ODOO_URL}")


if __name__ == "__main__":
    main()

