## $Id$
## CDSware User related utilities.

## This file is part of the CERN Document Server Software (CDSware).
## Copyright (C) 2002 CERN.
##
## The CDSware is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## The CDSware is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.  
##
## You should have received a copy of the GNU General Public License
## along with CDSware; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
This file implements all methods necessary for working with users and sessions in cdsware.
Contains methods for logging/registration when a user log/register into the system, checking if it
is a guest user or not.

At the same time this presents all the stuff it could need with sessions managements, working with websession.

It also contains Apache-related user authentication stuff.
"""

from dbquery import run_sql
import sys
import time
import os
import crypt
import string
import session
import websession
from websession import pSession, pSessionMapping
from config import *

def create_GuestUser():
    """Create a guest user , insert into user null values in all fields 

       create_GuestUser() -> GuestUserID
    """
    
    query_result = run_sql("insert into user (email) values ('')")
    return query_result

def getUid ( request ):
    """It gives the userId taking it from the cookie of the request,also has the control mechanism for the guest users,
       inserting in the MySql table when need it, and raise the cookie to the client.

       getUid(request) -> userId	 
    """
    sm = session.MPSessionManager(pSession, pSessionMapping())
    s = sm.get_session(request)
    userId = s.getUid()
    if userId == -1:# first time,create a guest_user
        id1 = create_GuestUser()
        s.setUid(id1)
        sm.maintain_session(request,s)
        return userId
    return userId

def setUid(request,uid):
    """It sets the userId into the session, and raise the cookie to the client.
    """
    sm = session.MPSessionManager(pSession, pSessionMapping())
    s = sm.get_session(request)
    s.setUid(uid)
    sm.maintain_session(request,s)
    
def isGuestUser(uid):
    """It Checks if the userId corresponds to a guestUser or not
      
       isGuestUser(uid) -> boolean
    """
    if uid==-1:
        return 1
    query_result = run_sql("select email from user where id=%s", (uid,))[0][0]
    if query_result == '':
        return 1
    return 0

def checkRegister(user,passw):
    """It checks if the user is register with the correct password
       
       checkRegister(user,passw) -> boolean
    """

    query_result = run_sql("select email,password from user where email=%s", (user,))
    if len(query_result)> 0 :
        return 0
    return 1

def checkemail(email):
    """It is a first intent for cheking the email,whith this first version it just checks if the email 
       written by the user doesn't contain blanks and that contains '@'
       
       checkemail(email) -> boolean
  """
    setArr = -1
    setSpac = 0
    for i in range(0,len(email)):
        if email[i] == '@':
            setArr =1
        if email[i]== ' ':
            setSpac =1
    if setArr==1 and setSpac==0:
        return 1
    return 0    

def getDataUid(request,uid):
    """It takes the email and password from a given userId, from the MySQL database, if don't exist it just returns
       guest values for email and password	
	
       getDataUid(request,uid) -> [email,password]

    """	

    email = 'guest'
    password = 'none'

    query_result = run_sql("select email, password from user where id=%s", (uid,))
    
    if len(query_result)>0:
        
        email = query_result[0][0]
        password = query_result[0][1]
        
    if password == None or  email =='':
        email = 'guest'
    list = [email] +[password]
    return list


def registerUser(request,user,passw):
    """It registers the user, inserting into the user table of MySQL database, the email and the pasword 
	of the user. It returns true if the insertion is done 
   
       registerUser(request,user,passw) -> boolean
    """
    if checkRegister(user,passw) and checkemail(user):
        query_result = run_sql("insert into user (email, password) values (%s,%s)", (user,passw))
        setUid(request,query_result)
        return 1
    return 0

def updateDataUser(req,uid,email,password):
    """It updates the data from the user. It is used when a user set his email and password
    """
    if email =='guest':
        return 0
    query_result = run_sql("update user set email=%s,password=%s where id=%s", (email,password,uid))
    
def loginUser(p_email,p_pw):
    """It is a first simple version for the authentication of user. It returns the id of the user, 
       for checking afterwards if the login is correct
    """
    query_result = run_sql("SELECT id from user where email=%s and password=%s", (p_email,p_pw))
    return query_result

def logoutUser(req,uid):
    """It logout the user of the system, creating a guest user.
    """
    sm = session.MPSessionManager(pSession, pSessionMapping())
    s = sm.get_session(req)
    id1 = create_GuestUser()
    s.setUid(id1)
    sm.maintain_session(req,s)

def userNotExist(p_email,p_pw):
    """Check if the user exits or not in the system
    """
    query_result = run_sql("select email from user where email=%s", (p_email,))
    if len(query_result)>0 and query_result[0]!='':
        return 0
    return 1

def update_Uid(req,p_email,p_pw,uid):
    """It updates the userId of the session. It is used when a guest user is logged in succesfully in the system 
    with a given email and password
    """	
    ## clean the guest user line which id = uid, previously inserted as guest user
    query_ID = int(run_sql("select id from user where email=%s and password=%s",
                           (p_email,p_pw))[0][0])
    setUid(req,query_ID)

def create_user_infobox(uid):
    """Create info box on currenly logged user.""" 
    out = ""
    out += """<table align="right" class="userinfobox">
               <tr>
                <td>
                 <strong>user:</strong> %s
                 ::
                 <a class="userinfobox" href="%s/youraccount.py/login">login</a>
                 ::
                 <a class="userinfobox" href="%s/youraccount.py/logout">logout</a>
                </td>
               </tr> 
              </table>""" % (getDataUid(None, uid)[0], weburl, weburl)
    return out

## --- follow some functions for Apache user/group authentication

def auth_apache_user_p(user, password):
    """Check whether user-supplied credentials correspond to valid
    Apache password data file.  Return 0 in case of failure, 1 in case
    of success."""    
    try:
        apache_password_line_for_user = os.popen("grep %s %s" % (user,cfg_apache_password_file), 'r').read()
        password_apache = string.split(string.strip(apache_password_line_for_user),":")[1]
    except: # no pw found, so return not-allowed status
        return 0
    salt = password_apache[:2]
    if crypt.crypt(password, salt) == password_apache:
        return 1
    else:
        return 0

def auth_apache_user_in_groups(user):
    """Return list of Apache groups to which Apache user belong."""
    out = []
    try:        
        pipe_input,pipe_output = os.popen2(["/bin/grep", user, cfg_apache_group_file], 'r')
        for line in pipe_output.readlines():
            out.append(string.split(string.strip(line),":")[0])
    except: # no groups found, so return empty list
        pass
    return out

def auth_apache_user_collection_p(user, password, coll):
    """Check whether user-supplied credentials correspond to valid
    Apache password data file, and whether this user is authorized to
    see the given collections.  Return 0 in case of failure, 1 in case
    of success."""    
    from search_engine import coll_restricted_p, coll_restricted_group
    if not auth_apache_user_p(user, password):
        return 0
    if not coll_restricted_p(coll):
        return 1
    if coll_restricted_group(coll) in auth_apache_user_in_groups(user):
        return 1
    else:
        return 0
