Apache
=========

This role is used to run Apache patching. It compares the version numbers, downloads the necessary files, creates a security email, and updates the repo, inorder to automate our patching workflow.


Requirements
------------

Server needs both Ansible and Python installed


Role Variables
--------------

paths: this variable is used to create a repo for the new patch files. This is usually an internal server of many directories. Needs a variable for every directory, so it can be created in the program.

tar_old: Should be initialized to false. It is used to see if the old directory is present in the file system.

zip_old: Should be initialized to false. It is used to see if the old directory is present in the file system.

zip: Should be initialized to false. It is used to see if the zip directory is present in the file system.

tar: Should be initialized to false. It is used to see if the tar directory is present in the file system.


Dependencies
------------

File paths are incorrect. They have been changed to protect sensitive company information. Proxies and emails have also been altered for this reason.


Example Playbook
----------------

Using the role, no variables need to be passed in
<br></br>
<br></br>
\- hosts: host2

  &nbsp; pre_tasks:
  <br></br>
    &nbsp; &nbsp; &nbsp;\- name: Install Beautiful Soup, requests, and urllib3 
    <br></br>
    &nbsp; &nbsp; &nbsp; &nbsp; pip: 
    <br></br>
     &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; name: beautifulsoup4, requests, urllib3
    <br></br>
     &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; state: present
    <br></br>
     &nbsp; &nbsp; &nbsp; &nbsp; delegate_to: localhost

  &nbsp; tasks:

   &nbsp; &nbsp; &nbsp;\- include_role: 
   <br></br>
   &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; name: corretto

   &nbsp; &nbsp; &nbsp;\- include_role:  
   &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; name: apache

   

License
-------

BSD


Author Information
------------------

Monica Schmidt

