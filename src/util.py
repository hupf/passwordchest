#
#  util.py
#  Password Chest
#
#  Created by Mathis Hofer on 18.10.09.
#  Copyright (c) 2009 Mathis Hofer. All rights reserved.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import re


def calculate_password_strength(password, username=None):
    score = 0 
    
    if password == '':
        return score
    
    if username and password.lower() == username.lower():
        return score
    
    # password length
    if len(password) < 5:
        score += 5
    elif len(password) > 4 and len(password) < 8:
        score += 10
    elif len(password) > 7:
        score +=25
    
    # letters
    lowerletters_count = len(re.findall('[a-z]', password))
    upperletters_count = len(re.findall('[A-Z]', password))
    if lowerletters_count and not upperletters_count:
        score += 10
    elif upperletters_count and upperletters_count:
        score += 20
    
    # numbers
    numbers_count = len(re.findall('\d', password))
    if numbers_count and numbers_count < 3:
        score += 10
    elif numbers_count >= 3:
        score += 20
    
    # special characters
    specialchars_count = len(re.findall('[^a-zA-Z0-9]', password))
    if specialchars_count == 1:
        score += 10
    elif specialchars_count > 1:
        score += 25
    
    # bonus
    if numbers_count and lowerletters_count:
        score += 2
    elif numbers_count and lowerletters_count and specialchars_count:
        score += 3
    elif numbers_count and upperletters_count and lowerletters_count and specialchars_count:
        score += 5
    
    return max(min(score, 100), 0)
