node {
  stage("Checkout") {
    checkout scm
  }
  stage("Build"){
    withCredentials([usernamePassword(credentialsId: 'Artifactory', usernameVariable: 'ARTI_NAME', passwordVariable: 'ARTI_PASS')]) {
        sh "docker build . -t ${docker2.imageRef()} --build-arg ARTI_NAME=$ARTI_NAME --build-arg ARTI_PASS=$ARTI_PASS"
    }
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
