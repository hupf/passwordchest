#
#  util.py
#  Password Chest
#
#  Created by Mathis Hofer on 18.10.09.
#  Copyright (c) 2009-2010 Mathis Hofer. All rights reserved.
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
import string
import urllib
from random import choice


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


def generate_random_password(length=10, use_uppercase=True, use_digits=False, use_punctuation=False):
    allowed_chars = string.ascii_lowercase
    if use_uppercase:
        allowed_chars += string.ascii_uppercase
    if use_digits:
        allowed_chars += string.digits
    if use_punctuation:
        allowed_chars += string.punctuation
    return ''.join([choice(allowed_chars) for i in range(length)])


def urlize(text):
    """
    Converts text to URL if possible.
    
    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.
    Modified by Mathis Hofer.

    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:

        1. Redistributions of source code must retain the above copyright notice, 
           this list of conditions and the following disclaimer.
        
        2. Redistributions in binary form must reproduce the above copyright 
           notice, this list of conditions and the following disclaimer in the
           documentation and/or other materials provided with the distribution.

        3. Neither the name of Django nor the names of its contributors may be used
           to endorse or promote products derived from this software without
           specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    """
    LEADING_PUNCTUATION  = ['(', '<', '&lt;']
    TRAILING_PUNCTUATION = ['.', ',', ')', '>', '\n', '&gt;']
    punctuation_re = re.compile('^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' % \
        ('|'.join([re.escape(x) for x in LEADING_PUNCTUATION]),
        '|'.join([re.escape(x) for x in TRAILING_PUNCTUATION])))
    simple_email_re = re.compile(r'^\S+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+$')
    
    text = text.strip()
    match = None
    if '.' in text or '@' in text or ':' in text:
        match = punctuation_re.match(text)
    if match:
        lead, middle, trail = match.groups()
        # Make URL we want to point to.
        url = None
        if middle.startswith('http://') or middle.startswith('https://'):
            url = urllib.quote(middle, safe='/&=:;#?+*')
        elif middle.startswith('www.') or ('@' not in middle and \
                middle and middle[0] in string.ascii_letters + string.digits and \
                (middle.endswith('.org') or middle.endswith('.net') or middle.endswith('.com'))):
            url = urllib.quote('http://%s' % middle, safe='/&=:;#?+*')
        elif '@' in middle and not ':' in middle and simple_email_re.match(middle):
            url = 'mailto:%s' % middle
        return url
    return text
