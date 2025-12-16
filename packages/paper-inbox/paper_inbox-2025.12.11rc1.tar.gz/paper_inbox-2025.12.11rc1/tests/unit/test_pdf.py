from unittest.mock import MagicMock, patch

import pytest

from paper_inbox.modules.pdf import exceptions, utils, validators


class TestPDFFunctions:
    """Test pdf functions"""

    example_output_libreoffice= '''
Title:           Some Title
Creator:         Writer
Producer:        LibreOffice 7.3
CreationDate:    Thu Jan  1 13:00:13 2026 GMT
Custom Metadata: no
Metadata Stream: no
Tagged:          no
UserProperties:  no
Suspects:        no
Form:            none
JavaScript:      no
Pages:           1
Encrypted:       no
Page size:       595.304 x 841.89 pts (A4)
Page rot:        0
File size:       29238 bytes
Optimized:       no
PDF version:     1.6
'''
    example_output_canva= '''
Title:           Some Title
Keywords:        keyword1,keyword2,0
Author:          Someone 
Creator:         Canva
Producer:        Canva
CreationDate:    Wed Jan  1 09:19:50 2026 GMT
ModDate:         Wed Jan  1 09:19:50 2026 GMT
Custom Metadata: no
Metadata Stream: no
Syntax Error: Suspects object is wrong type (boolean)
Tagged:          yes
UserProperties:  no
Suspects:        no
Form:            none
JavaScript:      no
Pages:           2
Encrypted:       no
Page size:       595.5 x 842.25 pts (A4)
Page rot:        0
File size:       103060 bytes
Optimized:       no
PDF version:     1.4
'''

    def test_is_canva_returns_false(self):
        with patch('paper_inbox.modules.pdf.utils.info_as_string') as mock_info_str:
            mock_info_str.return_value = str(self.example_output_libreoffice)
            result = utils.is_canva('placeholder_filepath')
            assert not result
    
    def test_is_canva_returns_true(self):
        with patch('paper_inbox.modules.pdf.utils.info_as_string') as mock_info_str:
            mock_info_str.return_value = str(self.example_output_canva)
            result = utils.is_canva('placeholder_filepath')
            assert result
    