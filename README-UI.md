# ontology-mapper-ui
The following information pertains to the text2term UI, which is written [here](https://github.com/ccb-hms/ontology-mapper-ui) and runs online [here](https://text2term.hms.harvard.edu/). It supports fewer features than the base package does, but provides a user interface for non-programmers.

### Running Locally via Node + Python

##### Requirements

-   Node >= 16.0.0
-   npm >= 8.0.0
-   Python >= 3.9.0
-   pip >= 21.0.0
-   text2term >= 1.1.0

**\*** These are the versions I have that work; while I know Python 3.9 or higher is necessary, the others may not strictly require the listed versions.

**\*\*** If you are running this locally on Google Chrome, you will likely run into issues with CORS (Cross-Origin Requests) that I have been unable to completely resolve. I would recommend using a different browser, using the Docker method, or finding some way to disable CORS on Chrome while running this.

#### Instructions

##### Initial Setup

When first cloned, run the command:


```
npm install
```

to install all necessary packages for the React frontend.

Next, go into the `flask-api` folder (perhaps by running `cd flask-api`) and run

```
pip install -r requirements-flask.txt
```

to install necessary packages for the Flask api.

##### Running

To run, make sure you are in the root of the repository and run, in two separate command line instances, the command

```
npm start
```

to start the front-end, which can be seen at `localhost:3000`, and the command

```
npm run flask-api
```

to start the back-end, which can be interacted with at `localhost:5000`.

### Running Locally via Docker

#### Requirements

-   Docker

#### Instructions

##### Initial Setup

Before running, make sure you have the latest version of the repository built by running the command

```
docker-compose build
```

Docker should build two images:

-   `ontology-mapper-api`: the Flask backend API
-   `ontology-mapper-client`: the React frontend

##### Running

To run the website, run the command:

```
docker-compose up
```

Docker should build two containers corresponding to the two images.

In a browser, navigate to `localhost:8602` to see the front-end.

### Acknowledgements

Initial setup of React and Flask and Dockerization aided by an [article series](https://blog.miguelgrinberg.com/post/how-to-dockerize-a-react-flask-project) by Miguel Grinberg.