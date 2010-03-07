# -*- coding: utf-8 -*-

#   This file is part of emesene.
#
#    Emesene is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    emesene is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with emesene; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

''' this file contains the AvatarManager class, used to manage Avatars ( really? :D ) '''

import os
import hashlib
import utils
import shutil

class AvatarManager(object):
    '''an utility class to manage avatars and their paths'''
    def __init__(self, session):
        '''constructor'''
        self.session = session
        self.config_dir = session.config_dir        
        self.config = session.config
        self.avatar_path = self.session.config.last_avatar

    def get_avatars_dir(self):
        ''' gets the user's avatar directory '''
        return self.config_dir.join(os.path.dirname(self.config_dir.base_dir),
                self.session.contacts.me.account.replace('@','-at-'),'avatars')        
    
    def get_cached_avatars_dir(self):
        ''' gets the contacts' cached avatar directory '''
        return self.config_dir.join(os.path.dirname(self.config_dir.base_dir),
                self.session.contacts.me.account.replace('@','-at-'),'cached_avatars')
    
    def get_system_avatars_dirs(self):
        ''' gets the directories where avatars are availables ( depending on the system ) '''
        faces_paths = []
        if os.name == 'nt':
            app_data_folder = os.path.split(os.environ['APPDATA'])[1]
            faces_path = os.path.join(os.environ['ALLUSERSPROFILE'], app_data_folder, \
                         "Microsoft", "User Account Pictures", "Default Pictures")
            #little hack to fix problems with encoding
            unicodepath = u"%s" % faces_path
            faces_paths = [unicodepath]
        else:
            faces_paths = ['/usr/share/kde/apps/faces', '/usr/share/kde4/apps/kdm/pics/users', \
                           '/usr/share/pixmaps/faces']
        return faces_paths

    def is_cached(self, filename):
        ''' check if a filename is already in one of the avatar caches '''
        bdir = os.path.dirname(filename)
        return bdir == self.get_avatars_dir() or \
            bdir == self.get_cached_avatars_dir() or \
            bdir in self.get_system_avatars_dirs()
    
    def set_as_avatar(self, filename):
        ''' set a picture as the current avatar and make a copy in the cache '''
        print 'setting ' + filename + ' as avatar'
        def gen_filename(source):
            ''' generate a unique (?) filename for the new avatar in cache, implemented as sha224 digest '''
            infile = open(source, 'rb')
            data = infile.read()
            infile.close()
            return hashlib.sha224(data).hexdigest()

        #i control if the filename is a already in cache
        if self.is_cached(filename):
            self.session.set_picture(filename)
            os.remove(self.avatar_path)
            shutil.copy2(filename, self.avatar_path)
            return
        #i save in 128*128 for the animation on connect..if somebody like it...:)
        try:
            fpath = os.path.join(self.get_avatars_dir(), gen_filename(filename))
            pix_128 = utils.safe_gtk_pixbuf_load(filename, (128, 128))
            pix_128.save(fpath, 'png')
            self.session.set_picture(fpath)
            if os.path.exists(self.avatar_path):
                os.remove(self.avatar_path)
            pix_128.save(self.avatar_path, 'png')
        except OSError, e:
            print e

