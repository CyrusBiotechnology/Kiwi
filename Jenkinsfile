node {
  stage("Build"){
    sh "docker build . -t ${docker2.imageRef()}"
  }
  
  stage ("Upload Image"){
    docker.autoPush()
  }
}
