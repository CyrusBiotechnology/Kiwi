node {
  stage("Checkout") {
    checkout scm
  }
  stage("Build"){
    sh "docker build . -t ${docker2.imageRef()}"
  }
  
  stage ("Upload Image"){
    docker.autoPush()
  }
  
  stage ("Deploy"){
    if (env.BRANCH_NAME in ['rc']) {
      k8s.updateImageTag(NAMESPACE, docker2.imageTag(), 'gcr.io/cyrus-containers/kiwi', env.BRANCH_NAME)
    }
  }
}
