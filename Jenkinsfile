pipeline {
    // agent { label 'Test_Node'}
    agent none
    stages {
        stage('Prepare') {
            agent { label 'Test_Node'}
            steps {
                echo "[*] Prepare Docker images..."
                sh 'python2 ./scripts/docker_build_push.py'
                echo "[+] Prepare Done!"
            }
        }
        stage('Test') {
            agent { label 'adworld'}
            when { branch "develop" }
            steps {
                echo "[*] Build all on Test Platform..."
                sh 'sh ./scripts/batch_import_challenges.sh /home/ubuntu/CTFd-swarm/import2chal.py'
                echo "[+] Build Done!"
            }
        }
        stage("Deploy") {
            agent { label 'adworld_production_host'}
            when { branch "deploy" }
            steps {
                echo "[*] Deploying..."
                sh 'sh ./scripts/batch_import_challenges.sh /home/cyberpeace/task_import.py'
                echo "[+] Deploy Done!"
            }
        }
    }
}
