cd ~/
apt-get install git-core -y
git clone https://github.com/italomaia/turtle-linux.git

cd ~/turtle-linux/setup/1404/32bits
chmod +x setup.sh
./setup.sh

cd ~/turtle-linux/dependencies
chmod +x install-avbin-linux-x86-64-v10
./install-avbin-linux-x86-64-v10

cd ~/turtle-linux/games
cp -r * /usr/games/

cd ~/turtle-linux/apps/vapor
python setup.py install

rm /usr/share/pixmaps/xubuntu-logo-menu.png
cp ~/turtle-linux/images/logo-menu.png /usr/share/pixmaps/xubuntu-logo-menu.png

cd /usr/share/xfce4/backdrops/
# remove xubuntu wallpapers
rm *.png
cp ~/turtle-linux/images/wallpaper/* /usr/share/xfce4/backdrops/
cd /usr/share/xfce4/backdrops/
# make turtle linux wallpaper the default wallpaper
ln -s 1366x768_by_dasAdam_adapted.png xubuntu-wallpaper.png

cp ~/turtle-linux/images/grub/turtle-background.png /boot/grub

# overwrite splash screen image
cp ~/turtle-linux/images/splash/wallpaper.png /lib/plymouth/themes/xubuntu-logo/wallpaper.png

rm -r ~/turtle-linux