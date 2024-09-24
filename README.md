# Projects
This is a docker deploy of demos of my personal projects

### Requirements:
```
sudo apt install -y curl git
curl -fsSL https://get.docker.com | sudo sh
```
### Install:
```
docker build -t projects https://github.com/procrastinando/projects.git#main:.
docker run -d -p 101:101 projects
```
