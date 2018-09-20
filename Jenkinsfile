node {
  stage("Checkout") {
    checkout scm
  }
  stage("Build"){
    sh "docker build . -t ${docker2.imageRef()}"
  }
  
  stage ("Upload Image"){
    docker2.autoPush()
  }
  
  stage ("Deploy"){
    NAMESPACE = k8s.getNamespaceFromBranch(env.BRANCH_NAME)
    if (env.BRANCH_NAME in ['rc']) {
      k8s.updateImageTag(NAMESPACE, docker2.imageTag(), 'gcr.io/cyrus-containers/kiwi', env.BRANCH_NAME)
    }
  }
}
