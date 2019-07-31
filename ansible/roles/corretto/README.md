Corretto
=========

This role is used to run Corretto patching. It compares the version numbers, downloads the necessary files, creates a security email, and updates the repo, inorder to automate our patching workflow.


Requirements
------------

Server needs both Ansible and Python installed


Role Variables
--------------

paths: This variable is used to create a repo for the new patch files. This is usually an internal server of many directories. Needs a variable for every directory, so it can be created in the program.

linux_dir_deats: Should be initialized to false. It is used to see if the linux directory is present in the file system.

windows_dir_deats: Should be initialized to false. It is used to see if the windows directory is present in the file system.

version_output: This is used to create different file paths based on dynamic information

linux_dir: Should be initialized to false. It is used to see if the linux directory is present in a different file system.

windows_dir: Should be initialized to false. It is used to see if the linux directory is present in a different file system.

arg: Should be initialized to 8 or 11. It is used to specify which version of corretto is being used.


Dependencies
------------

File paths are incorrect. They have been changed to protect sensitive company information. Proxies and emails have also been altered for this reason.


Example Playbook
----------------

Using the role, no variables need to be passed in.
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
   &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; name: corretto

   &nbsp; &nbsp; &nbsp;\- include_role:  
   &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; name: apache


License
-------

BSD


Author Information
------------------

Monica Schmidt

