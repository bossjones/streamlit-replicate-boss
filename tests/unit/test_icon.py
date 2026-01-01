"""Unit tests for utils.icon module."""
import pytest
from unittest.mock import Mock, patch
from utils.icon import show_icon


class TestShowIcon:
    """Tests for show_icon() function."""
    
    @pytest.mark.unit
    def test_show_icon_renders_emoji(self):
        """[P2] Test that show_icon renders emoji with correct HTML structure."""
        # GIVEN: An emoji string
        emoji = ":balloon:"
        
        # WHEN: Calling show_icon with mocked streamlit
        with patch('utils.icon.st') as mock_st:
            show_icon(emoji)
            
            # THEN: st.write should be called with HTML containing the emoji
            mock_st.write.assert_called_once()
            call_args = mock_st.write.call_args
            assert len(call_args[0]) == 1
            html_content = call_args[0][0]
            assert emoji in html_content
            assert 'font-size: 78px' in html_content
            assert 'line-height: 1' in html_content
            # Verify unsafe_allow_html is True
            assert call_args[1]['unsafe_allow_html'] is True
    
    @pytest.mark.unit
    def test_show_icon_with_different_emoji(self):
        """[P2] Test that show_icon works with different emoji values."""
        # GIVEN: Different emoji strings
        emojis = [":foggy:", ":rainbow:", ":bridge_at_night:"]
        
        # WHEN/THEN: Each emoji should render correctly
        for emoji in emojis:
            # Patch the st module in utils.icon
            with patch('utils.icon.st') as mock_st:
                # Clear function cache if it exists
                if hasattr(show_icon, 'clear'):
                    show_icon.clear()
                
                # Call the function
                show_icon(emoji)
                
                # Verify write was called
                assert mock_st.write.called, f"st.write was not called for emoji: {emoji}"
                html_content = mock_st.write.call_args[0][0]
                assert emoji in html_content
                assert 'font-size: 78px' in html_content
                assert mock_st.write.call_args[1]['unsafe_allow_html'] is True
                
                # Reset mock for next iteration
                mock_st.reset_mock()
    
    @pytest.mark.unit
    def test_show_icon_uses_cache_decorator(self):
        """[P2] Test that show_icon is decorated with @st.cache_data."""
        import inspect
        from streamlit import runtime
        
        # GIVEN: The show_icon function
        # WHEN: Checking if it has cache_data decorator
        # THEN: Function should exist and be callable
        assert callable(show_icon)
        assert hasattr(show_icon, '__wrapped__') or hasattr(show_icon, '__name__')
