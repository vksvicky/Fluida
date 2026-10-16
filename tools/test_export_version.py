"""Store export bumps only the application version and keeps release notes plain."""

import unittest

from export_version import apply_bump, release_notes

MANIFEST = """<?xml version="1.0"?>
<iq:manifest xmlns:iq="http://www.garmin.com/xml/connectiq" version="3">
    <iq:application entry="FluidaApp" id="c4f828a1-5998-4920-bb37-9a2f778a4e91" version="0.1.0">
    </iq:application>
</iq:manifest>
"""


class ExportVersionTests(unittest.TestCase):
    def test_patch_minor_and_major_leave_the_manifest_schema_alone(self):
        patched, version = apply_bump(MANIFEST, "patch")
        self.assertEqual(version, "0.1.1")
        self.assertIn('version="3"', patched)
        self.assertIn('version="0.1.1"', patched)
        self.assertNotIn('version="0.1.0"', patched)

        _, minor = apply_bump(MANIFEST, "minor")
        _, major = apply_bump(MANIFEST, "major")
        self.assertEqual(minor, "0.2.0")
        self.assertEqual(major, "1.0.0")

    def test_custom_version_and_skip(self):
        updated, version = apply_bump(MANIFEST, "custom", "1.4.2")
        self.assertEqual(version, "1.4.2")
        self.assertIn('version="1.4.2"', updated)

        skipped, same = apply_bump(MANIFEST, "skip")
        self.assertEqual(same, "0.1.0")
        self.assertEqual(skipped, MANIFEST)

    def test_release_notes_tell_an_owner_what_the_face_does(self):
        notes = release_notes("0.2.0")
        self.assertIn("What's New in v0.2.0:", notes)
        self.assertIn("fluid columns", notes)
        self.assertIn("temperature", notes)
        self.assertNotIn("refactor", notes.lower())
        self.assertNotIn(".mc", notes)
        self.assertTrue(notes.isascii())
