# Fortishield Filebeat module

## Hosting

The Fortishield Filebeat module is hosted at the following URLs

- Production:
  - https://packages.fortishield.com/4.x/filebeat/
- Development:
  - https://packages-dev.fortishield.com/pre-release/filebeat/
  - https://packages-dev.fortishield.com/staging/filebeat/

The Fortishield Filebeat module must follow the following nomenclature, where revision corresponds to X.Y values

- fortishield-filebeat-{revision}.tar.gz

Currently, we host the following modules

|Module|Version|
|:--|:--|
|fortishield-filebeat-0.1.tar.gz|From 3.9.x to 4.2.x included|
|fortishield-filebeat-0.2.tar.gz|From 4.3.x to 4.6.x included|
|fortishield-filebeat-0.3.tar.gz|4.7.x|
|fortishield-filebeat-0.4.tar.gz|From 4.8.x to current|


## How-To update module tar.gz file

To add a new version of the module it is necessary to follow the following steps:

1. Clone the fortishield/fortishield repository
2. Check out the branch that adds a new version
3. Access the directory: **extensions/filebeat/7.x/fortishield-module/**
4. Create a directory called: **fortishield**

```
# mkdir fortishield
```

5. Copy the resources to the **fortishield** directory

```
# cp -r _meta fortishield/
# cp -r alerts fortishield/
# cp -r archives fortishield/
# cp -r module.yml fortishield/
```

6. Set **root user** and **root group** to all elements of the **fortishield** directory (included)

```
# chown -R root:root fortishield
```

7. Set all directories with **755** permissions

```
# chmod 755 fortishield
# chmod 755 fortishield/alerts
# chmod 755 fortishield/alerts/config
# chmod 755 fortishield/alerts/ingest
# chmod 755 fortishield/archives
# chmod 755 fortishield/archives/config
# chmod 755 fortishield/archives/ingest
```

8. Set all yml/json files with **644** permissions

```
# chmod 644 fortishield/module.yml
# chmod 644 fortishield/_meta/config.yml
# chmod 644 fortishield/_meta/docs.asciidoc
# chmod 644 fortishield/_meta/fields.yml
# chmod 644 fortishield/alerts/manifest.yml
# chmod 644 fortishield/alerts/config/alerts.yml
# chmod 644 fortishield/alerts/ingest/pipeline.json
# chmod 644 fortishield/archives/manifest.yml
# chmod 644 fortishield/archives/config/archives.yml
# chmod 644 fortishield/archives/ingest/pipeline.json
```

9. Create **tar.gz** file

```
# tar -czvf fortishield-filebeat-0.4.tar.gz fortishield
```

10. Check the user, group, and permissions of the created file

```
# tree -pug fortishield
[drwxr-xr-x root     root    ]  fortishield
├── [drwxr-xr-x root     root    ]  alerts
│   ├── [drwxr-xr-x root     root    ]  config
│   │   └── [-rw-r--r-- root     root    ]  alerts.yml
│   ├── [drwxr-xr-x root     root    ]  ingest
│   │   └── [-rw-r--r-- root     root    ]  pipeline.json
│   └── [-rw-r--r-- root     root    ]  manifest.yml
├── [drwxr-xr-x root     root    ]  archives
│   ├── [drwxr-xr-x root     root    ]  config
│   │   └── [-rw-r--r-- root     root    ]  archives.yml
│   ├── [drwxr-xr-x root     root    ]  ingest
│   │   └── [-rw-r--r-- root     root    ]  pipeline.json
│   └── [-rw-r--r-- root     root    ]  manifest.yml
├── [drwxr-xr-x root     root    ]  _meta
│   ├── [-rw-r--r-- root     root    ]  config.yml
│   ├── [-rw-r--r-- root     root    ]  docs.asciidoc
│   └── [-rw-r--r-- root     root    ]  fields.yml
└── [-rw-r--r-- root     root    ]  module.yml
```

11. Upload file to development bucket
