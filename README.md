# OpenSea Collection Download Tool
Python (FastAPI, Mongo) server with manual async task execution for downloading the metadata of an opensea collection and calculating rarity values.

## Example Client Code

    jobId = post("http://localhost:8000/api/collections/<CollectionName>/download")
	
	status = get("http://localhost:8000/api/jobs/"+jobId).status
	while status  != "FINISHED":
		status = get("http://localhost:8000/api/jobs/"+jobId).status
	
	# Distribution gives rarity information on each trait, and for each token as a whole
	distribution = get("http://localhost:8000/api/collections/<CollectionName>/distribution")
	
		

