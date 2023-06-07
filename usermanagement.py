'''

@author: rnatarajan
https://github.com/rathnapandi

'''
import sys
import os

from optparse import OptionParser

from com.vordel.domain.rbac import AdminUserStoreDAO
from com.vordel.domain.rbac import AdminUser
from com.vordel.api.adminusers.model import AdminUserStore

from com.fasterxml.jackson.databind import ObjectMapper
from java.io import FileReader, File
from java.lang import String
from java.util import TreeSet

if __name__ == '__main__':

    parser = OptionParser(prog="usermanagement",
                          description="Manage API Gateway Manager (ANM) Users ")
    parser.add_option('--action', dest='action', help='What to do with the user.  Valid actions are: add, update, and delete.')
    parser.add_option('--username', dest='username', help='Username')
    parser.add_option('--password', dest='password', help='Password')
    parser.add_option('--filePath', dest='filePath', help='Path to the adminUsers.json file, e.g /opt/Axway/apigateway/conf/adminUsers.json')
    parser.add_option('--roles', dest='roles', help='Comma separated list of numbers representing roles.  Default roles are: \n 1. API Server Administrator \n 2. API Server Operator \n 3. Deployer \n 4. KPS Administrator \n 5. Policy Developer ')
    (options, args) = parser.parse_args()
    print "Running user management script with options: " + str(options)

    action = getattr(options, 'action')
    username = getattr(options, 'username')
    password = getattr(options, 'password')
    filePath = getattr(options, 'filePath')
    if(filePath is None):
        print "Specifying a filePath for the adminUsers.json file is mandatory."
        sys.exit(1)

    if(action is None):
        if(username is None or password is None):
            print "Please provide a username and a password."
            sys.exit(1)
        store = AdminUserStoreDAO()
        store.createInitialAdminUserStore(username, String(password).toCharArray())
        store.write(File(filePath).getParentFile())
    else:
        roles = getattr(options, 'roles')
        rolesDictionary = {'1':'API Server Administrator', '2': 'API Server Operator', '3': 'Deployer', '4': 'KPS Administrator', '5': 'Policy Developer' }
        objectMapper = ObjectMapper()
        adminUserStore = objectMapper.readValue(FileReader(filePath), AdminUserStore)
        if(action.lower() == 'add'):
            print "Adding a new user..."
            rolesIds = TreeSet()
            rolesArray = roles.split(',')
            for role in rolesArray:
                roleDesc = rolesDictionary[role]
                roleObj = adminUserStore.getAdminUserRoleByName(roleDesc)
                rolesIds.add(roleObj.getId())
            admin = adminUserStore.addAdminUser(username, rolesIds)
            if(admin is None):
                print "User " + username + " already exists, please provide a unique username."
                sys.exit(1)
            adminUserStore.incrementVersion()
            adminUserStore.storePassword(admin.getId(), String(password).toCharArray())
            adminUserStore.write(File(filePath).getParentFile())
            print "Added new user " + username + " with roles: " + roleDesc
        elif(action.lower() == 'update'):
            print "Updating user..."
            rolesIds = TreeSet()
            adminUser = adminUserStore.getAdminUserByName(username)
            if( adminUser is None):
                print "User " + username + " does not exist, please provide an existing username to update."
                sys.exit(1)
            rolesArray = roles.split(',')
            for role in rolesArray:
                roleDesc = rolesDictionary[role]
                roleObj = adminUserStore.getAdminUserRoleByName(roleDesc)
                rolesIds.add(roleObj.getId())
            adminUserStore.storePassword(adminUser.getId(), String(password).toCharArray())
            adminUser.setRoles(rolesIds)
            adminUserStore.incrementVersion()
            adminUserStore.write(File(filePath).getParentFile())
            print "Updated user " + username + " with roles " + roleDesc
        elif(action.lower() == 'delete'):
            print "Deleting user..."
            adminUser = adminUserStore.getAdminUserByName(username)
            if( adminUser is None):
                print "User " + username + " does not exist, please provide an existing username to delete."
                sys.exit(1)
            adminUsers = adminUserStore.getAdminUsers()
            adminUserCredentials = adminUserStore.getAdminUserCredentials()
            userRemoveStatus = adminUsers.remove(adminUser)
            userCredRemoveStatus = adminUserCredentials.remove(adminUser.getId())
            if( userRemoveStatus is None and userCredRemoveStatus != None):
                adminUserStore.incrementVersion()
                adminUserStore.write(File(filePath).getParentFile())
                print "User " + username + " deleted."
        else:
            print "Invalid action: " + action + ".  Valid actions are:  add, update & delete."
            sys.exit(1)
pass