# Clone directory
apt-get update
apt-get install -y git
apt-get install -y build-essential  
apt-get install -y gcc
apt install ffmpeg -y
apt-get install -y wget

# Clone git
git clone https://github.com/TMElyralab/MusePose.git
mv MusePose muse_pose

# Create assets dir
mkdir -p /muse_pose/assets/videos && mkdir -p /muse_pose/assets/images && mkdir -p /muse_pose/assets/audios && mkdir -p /muse_pose/assets/poses/

# Install git-lfs
apt-get install -y git-lfs
git lfs install
