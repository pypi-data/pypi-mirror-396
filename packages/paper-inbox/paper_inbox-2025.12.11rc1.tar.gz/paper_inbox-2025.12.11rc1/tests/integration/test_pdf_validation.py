import os
import shutil
from pathlib import Path

import pytest

from paper_inbox.modules.pdf import exceptions, utils, validators


class TestPDFFunctions:
    """ pdf functions integration tests """

    d = Path(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures'))
    valid = d / "valid.pdf"
    canva = d / "canva.pdf"
    html = d / "html.pdf"
    invalid_trailer = d / "invalid_trailer.pdf"
    missing_endobj = d / "missing_endobj.pdf"
    missing_eof = d / "missing_eof.pdf"
    no_xref = d / "no_xref.pdf"
    wrong_offsets = d / "wrong_offsets.pdf"
    wrong_mimetype = d / "wrong_mimetype.png"
    wrong_magicheader = d / "wrong_magicheader.pdf"
    valid_with_syntax_error = d / "valid_syntaxerror.pdf"
        
    def test_is_valid(self):
        assert utils.is_valid(self.valid)
        assert utils.is_valid(self.canva)
        assert not utils.is_valid(self.invalid_trailer)
        assert not utils.is_valid(self.missing_endobj)
        assert not utils.is_valid(self.missing_eof)
        assert not utils.is_valid(self.no_xref)
        assert not utils.is_valid(self.wrong_offsets)
    
    def test_is_canva(self):
        assert utils.is_canva(self.canva)
        assert not utils.is_canva(self.valid)

    def test_validate_mimetype(self):
        with pytest.raises(exceptions.InvalidMimeType):
            validators.validate_mime_type(self.wrong_mimetype)
        validators.validate_mime_type(self.valid)

    def test_validate_magic_header(self):
        with pytest.raises(exceptions.MalformedMagicHeader):
            validators.validate_magic_header(self.wrong_magicheader)
        validators.validate_magic_header(self.valid)

    def test_validate_file_head(self):
        with pytest.raises(exceptions.MalformedFileHead):
            validators.validate_file_head(self.wrong_magicheader)
        validators.validate_file_head(self.valid)

    def test_validate_not_html(self):
        with pytest.raises(exceptions.InvalidDataTypeHTML):
            validators.validate_not_html(self.html)
        validators.validate_not_html(self.valid)

    def test_validate_structure(self):
        with pytest.raises(exceptions.SyntaxErrorInPDFStructure):
            validators.validate_structure(self.missing_endobj)
        with pytest.raises(exceptions.SyntaxErrorInPDFStructure):
            validators.validate_structure(self.no_xref)
        validators.validate_structure(self.valid)

    def test_fix_pdf(self):
        tmp_dir = self.d / 'tmp'
        tmp_dir.mkdir(parents=True, exist_ok=True)
        test_path = tmp_dir / 'test.pdf'
        shutil.copy(self.valid_with_syntax_error, test_path)

        ## assert applied fix works
        assert not utils.is_valid(test_path)
        utils.fix_pdf(test_path)
        assert utils.is_valid(test_path)

        ## cleanup
        _ = [f.unlink() for f in tmp_dir.iterdir() if f.is_file()]
        tmp_dir.rmdir()