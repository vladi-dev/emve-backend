# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "chef/freebsd-10.0"
  config.ssh.forward_agent = true
  config.ssh.shell = 'sh'
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.synced_folder ".", "/vagrant", type: "nfs", id: "vagrant-root"
  config.vm.provider :virtualbox do |vb|
    #vb.gui = true
  end
end
