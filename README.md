### Start this repository 
- The folliwng will start this registry on port 8888
  
  `python -m https 8888`

- Or serve it with docker over nginx like so

  ```
  schema-repository:
    image: nginx:latest
    ports:
      - "8888:8888"
    volumes:
      - ../kafka-schema-registry/:/usr/share/nginx/html:ro
  ```

- And you will be able to reference it in a pom.xml when served as

  ```
  <repositories>
      <repository>
          <id>local-app-repo</id>
          <url>http://localhost:8888</url>
      </repository>
  </repositories>
  ```
  
- Then packages served here can be accessed as such in the pom
  ```
  <dependency>
      <groupId>com.demo.schema</groupId>
      <artifactId>schema_library</artifactId>
      <version>1.0-SNAPSHOT</version>
  </dependency>
  ```

### Add a package to the registry
    `./grab_latest.py -pd PROJECT_DIRECTORY -rd THIS_DIRECTORY`
