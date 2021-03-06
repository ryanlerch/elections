#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 (c) 2014 - Copyright Pierre-Yves Chibon
 Author: Pierre-Yves Chibon <pingou@pingoured.fr>

# This copyrighted material is made available to anyone wishing to use, modify,
# copy, or redistribute it subject to the terms and conditions of the GNU
# General Public License v.2, or (at your option) any later version.  This
# program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the GNU
# General Public License along with this program; if not, write to the Free
# Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA. Any Red Hat trademarks that are incorporated in the source
# code or documentation are not subject to the GNU General Public License and
# may only be used or replicated with the express permission of Red Hat, Inc.

 fedora_elections.elections test script
"""
__requires__ = ['SQLAlchemy >= 0.7', 'jinja2 >= 2.4']
import pkg_resources

import logging
import unittest
import sys
import os

from datetime import time
from datetime import timedelta

import flask

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import fedora_elections
from tests import ModelFlasktests, Modeltests, TODAY, FakeUser, user_set


# pylint: disable=R0904
class FlaskSimpleElectionstests(ModelFlasktests):
    """ Flask application tests range voting. """

    def test_vote_select(self):
        """ Test the vote_select function - the preview part. """
        output = self.app.get(
            '/vote/test_election', follow_redirects=True)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>OpenID transaction in progress</title>' in output.data
            or 'discoveryfailure' in output.data)

        self.setup_db()

        user = FakeUser(['packager'], username='pingou')
        with user_set(fedora_elections.APP, user):
            output = self.app.get(
                '/vote/test_election6')
            self.assertTrue(
                'test election 6 shortdesc' in output.data)
            self.assertTrue(
                '<input type="hidden" name="action" value="preview" />'
                in output.data)

            csrf_token = output.data.split(
                'name="csrf_token" type="hidden" value="')[1].split('">')[0]

            # Invalid vote: No candidate
            data = {
                'action': 'preview',
            }

            output = self.app.post('/vote/test_election6', data=data)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                'test election 6 shortdesc' in output.data)

            # Invalid vote: Too many candidates
            data = {
                'Kevin': True,
                'Toshio': True,
                'action': 'preview',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/vote/test_election6', data=data)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                'test election 6 shortdesc' in output.data)
            self.assertTrue(
                '<input type="hidden" name="action" value="preview" />'
                in output.data)
            self.assertTrue(
                'Too many candidates submitted'
                in output.data)

            # Valid input
            data = {
                'Kevin': True,
                'action': 'preview',
                'csrf_token': csrf_token,
            }

            output = self.app.post('/vote/test_election6', data=data)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                'test election 6 shortdesc' in output.data)
            self.assertTrue(
                '<input type="hidden" name="action" value="submit" />'
                in output.data)
            self.assertTrue(
                'Please confirm your vote!'
                in output.data)

    def test_vote_select_process(self):
        """ Test the vote_select function - the voting part. """
        output = self.app.get(
            '/vote/test_election', follow_redirects=True)
        self.assertEqual(output.status_code, 200)
        self.assertTrue(
            '<title>OpenID transaction in progress</title>' in output.data
            or 'discoveryfailure' in output.data)

        self.setup_db()

        user = FakeUser(['packager'], username='pingou')
        with user_set(fedora_elections.APP, user):
            # Invalid candidate id - no csrf
            data = {
                'candidate': 1,
                'action': 'submit',
            }

            output = self.app.post(
                '/vote/test_election6', data=data,
                follow_redirects=True)
            self.assertEqual(output.status_code, 200)

            csrf_token = output.data.split(
                'name="csrf_token" type="hidden" value="')[1].split('">')[0]

            # Valid input
            data = {
                'Toshio': True,
                'action': 'submit',
                'csrf_token': csrf_token,
            }

            output = self.app.post(
                '/vote/test_election6', data=data,
                follow_redirects=True)
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                'Your vote has been recorded.  Thank you!'
                in output.data)
            self.assertTrue('Open elections' in output.data)

    def test_vote_select_revote(self):
        """ Test the vote_select function - the re-voting part. """
        #First we need to vote
        self.setup_db()

        user = FakeUser(['voters'], username='nerdsville')
        with user_set(fedora_elections.APP, user):
            retrieve_csrf = self.app.post('/vote/test_election6')
            csrf_token = retrieve_csrf.data.split(
                'name="csrf_token" type="hidden" value="')[1].split('">')[0]

            # Valid input
            data = {
                'Kevin': True,
                'action': 'submit',
                'csrf_token': csrf_token,
            }
            self.app.post('/vote/test_election6', data=data, follow_redirects=True)
            vote = fedora_elections.models.Vote
            votes = vote.of_user_on_election(self.session, "nerdsville", '6')
            self.assertEqual(votes[0].candidate.name, "Toshio")
            self.assertEqual(votes[0].value, 0)
            self.assertEqual(votes[1].candidate.name, "Kevin")
            self.assertEqual(votes[1].value, 1)

            #Next, we need to try revoting
            newdata = {
                'Toshio': True,
                'action': 'submit',
                'csrf_token': csrf_token,
            }
            output = self.app.post('/vote/test_election6', data=newdata, follow_redirects=True)
            #Next, we need to check if the vote has been recorded
            self.assertEqual(output.status_code, 200)
            self.assertTrue(
                'Your vote has been recorded.  Thank you!'
                in output.data)
            self.assertTrue('Open elections' in output.data)
            vote = fedora_elections.models.Vote
            votes = vote.of_user_on_election(self.session, "nerdsville", '6')
            self.assertEqual(votes[0].value, 1)
            self.assertEqual(votes[1].value, 0)


        #If we haven't failed yet, HOORAY!


if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(
        FlaskSimpleElectionstests)
    unittest.TextTestRunner(verbosity=2).run(SUITE)
