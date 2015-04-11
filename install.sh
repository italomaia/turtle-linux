apt-get install git-core
git clone git@github.com:italomaia/turtle-linux.git

cd turtle-linux/setup/1404/32bits
chmod +x setup.sh
./setup.sh

cd ../../../dependencies
chmod +x install-avbin-linux-x86-64-v10
./install-avbin-linux-x86-64-v10

cd ../games
cp -r * /usr/games/