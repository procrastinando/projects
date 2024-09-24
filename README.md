# Projects
This is a docker deploy of demos of my personal projects

### Requirements:
```
sudo apt install -y curl git
curl -fsSL https://get.docker.com | sudo sh
```
### Build the image:
- Locally: `docker build -t projects .`
- From the repository: `docker build -t projects https://github.com/procrastinando/projects.git#main:.`
### Option 1: Run by command:
```
docker run -d -p 50001:50001 -p 50002:50002 projects
```
### Option 2: Run it as stack:
```
services:
  app:
    image: projects
    ports:
      - "50001:50001"
      - "50002:50002"
    restart: unless-stopped
```
