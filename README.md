# EMT User Management

By design the Axway API Gateway's Elastic Managed Topology (EMT) mode does not allow user management for users of the API Gateway Manager / Admin Node Manager (ANM) because they are stored in a static file named `adminUsers.json` that is baked into the image.  This requires you to set up an authentication repository like LDAP to manage the users externally, which is too much overhead for some projects.  This Jython script helps automate manipulation of the user store, letting you create, update and delete users from the file.

The script is intended to be executed inside the Docker container and the required files like adminUsers.json and usermanagement.py should be mounted using Docker volumes.

## Help Command Output

```
Usage: usermanagement [options]

Manage API Gateway Manager (ANM) Users

Options:

  -h, --help           Show this help message and exit.
  --action=ACTION      What to do with the user.  Valid actions are: add, update, and delete.
  --username=USERNAME  Username
  --password=PASSWORD  Password
  --filePath=FILEPATH  Path to the adminUsers.json file path e.g
                       /opt/Axway/apigateway/conf/adminUsers.json
  --roles=ROLES        Comma separated list of numbers representing roles.
                       Default roles are:   
                       1. API Server Administrator
                       2. API Server Operator   
                       3. Deployer   
                       4. KPS Administrator 
                       5. Policy Developer                 
```

If you have defined custom roles, or otherwise changed the roles list, note that you may have to customize the list of role mappings in this script in the `rolesDictionary` object to make it work.  Also note that the numbers in the `--roles` argument are relative, so a `3` corresponds to the third role defined in `adminUsers.json` which might not match up with what's listed as `role-3` in the `adminUsers.json` file.  If the `adminUsers.json` file contains a list like `role-1`, `role-2`, `role-5`, `role-6`, and `role-7`, then `--roles=1,2,3` will give the user `"roles" : [ "role-1", "role-2", "role-5" ]` in the output.

For more information on how RBAC works and these user roles are defined in the API Gateway, refer to the Axway API Gateway documentation on how to [Configure Role-Based Access Control (RBAC)](https://docs.axway.com/bundle/axway-open-docs/page/docs/apim_administration/apigtw_admin/general_rbac/index.html).

## Examples

*Update user*

`docker run -it  -v /Users/rnatarajan/APIM/apigw-emt-scripts-2.1.0-SNAPSHOT/Dockerfiles/emt-nodemanager:/home/axway/scripts apigw-base:latest /bin/bash /opt/Axway/apigateway/posix/bin/jython /home/axway/scripts/usermanagement.py --filePath=/home/axway/scripts/conf/adminUsers.json --username admin2 --password changeme --action update --roles 1,2,3,4,5`

*Delete User*

`docker run -it  -v /Users/rnatarajan/APIM/apigw-emt-scripts-2.1.0-SNAPSHOT/Dockerfiles/emt-nodemanager:/home/axway/scripts apigw-base:latest /bin/bash /opt/Axway/apigateway/posix/bin/jython /home/axway/scripts/usermanagement.py --filePath=/home/axway/scripts/conf/adminUsers.json --username admin2 --action delete`

*Add User*

`docker run -it  -v /Users/rnatarajan/APIM/apigw-emt-scripts-2.1.0-SNAPSHOT/Dockerfiles/emt-nodemanager:/home/axway/scripts apigw-base:latest /bin/bash /opt/Axway/apigateway/posix/bin/jython /home/axway/scripts/usermanagement.py --filePath=/home/axway/scripts/conf/adminUsers.json --username admin2 --password changeme --action add --roles 1,2,3`

*Default User Creation*

`docker run -it  -v /Users/rnatarajan/APIM/apigw-emt-scripts-2.1.0-SNAPSHOT/Dockerfiles/emt-nodemanager:/home/axway/scripts apigw-base:latest /bin/bash /opt/Axway/apigateway/posix/bin/jython /home/axway/scripts/usermanagement.py --filePath=/home/axway/scripts/conf/adminUsers.json --username admin2 --password changeme`

Then you have to copy the `adminUsers.json` file during ANM container creation.  This is accomplished via the `COPY --chown=emtuser conf/adminUsers.json /opt/Axway/apigateway/conf` command in the sample below:

```bash
ARG PARENT_IMAGE
FROM $PARENT_IMAGE

ARG DOCKER_IMAGE_ID
ARG ANM_USERNAME
ARG HEALTHCHECK
ARG METRICS_DB_URL
ARG METRICS_DB_USERNAME
ARG FIPS_MODE

COPY --chown=emtuser opt/emt_resources /opt/emt
COPY --chown=emtuser scripts/* /opt/Axway/apigateway/posix/bin/
COPY --chown=emtuser conf/adminUsers.json /opt/Axway/apigateway/conf

USER emtuser
RUN if [ -e /opt/emt/lic.lic ]; then cp /opt/emt/lic.lic /opt/Axway/apigateway/conf/licenses; fi && \
if [ "$HEALTHCHECK" = "True" ]; then cp /opt/emt/anm_hc_path.xml /opt/Axway/apigateway/samples/SamplePolicies/HealthCheck; fi && \
mkdir -p /opt/Axway/apigateway/groups/certs/private && \
touch /opt/Axway/apigateway/groups/certs/index.txt && \
echo $(printf '%x\n' `date +"%s%2N"`) > /opt/Axway/apigateway/groups/certs/serial && \
cp /opt/emt/domaincert.pem /opt/Axway/apigateway/groups/certs/ && \
cp /opt/emt/domainkey.pem /opt/Axway/apigateway/groups/certs/private/ && \
cd /opt/Axway/apigateway/posix/bin && \
./setup-emt-nodemanager \
--props /opt/emt/config.props \
--fed /opt/emt/fed.fed \
--anm-username "$ANM_USERNAME" \
--merge-dir /opt/emt/apigateway \
--healthcheck $HEALTHCHECK \
--docker-image-id "$DOCKER_IMAGE_ID" \
--metrics-db-url "$METRICS_DB_URL" \
--metrics-db-username "$METRICS_DB_USERNAME" \
--fips $FIPS_MODE && \
rm -rf /opt/emt \
rm -rf /opt/Axway/apigateway/tools/sdk-generator \
rm -rf /opt/Axway/APIM/apigateway/samples \
rm -rf /opt/Axway/APIM//apigateway/system/lib/ibmmq

CMD ["/opt/Axway/apigateway/posix/bin/start-emt-nodemanager"]
```

## Authorship

This script was authored by my colleague [Rathna Natarajan](https://github.com/rathnapandi) who gave me permission to host this script here and license it under the Apache license.
