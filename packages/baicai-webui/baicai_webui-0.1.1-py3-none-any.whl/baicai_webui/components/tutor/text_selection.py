import streamlit as st
import streamlit.components.v1 as components


def text_selection_detector(text):
    """A component that detects text selection using drag events and supports markdown."""

    # Initialize session state if not exists
    if "selected_text" not in st.session_state:
        st.session_state.selected_text = ""

    # Display the text using markdown
    st.markdown(text)

    # JavaScript code to detect text selection using drag
    js_code = """
    <script>
    let isDragging = false;
    let startX, startY;
    let selectedText = '';

    function handleDragStart(e) {
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        selectedText = '';
    }

    function handleDrag(e) {
        if (isDragging) {
            const selection = window.getSelection();
            selectedText = selection.toString();
        }
    }

    function handleDragEnd(e) {
        isDragging = false;
        if (selectedText) {
            // Send the selected text to Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: selectedText
            }, '*');
        }
    }

    // Add event listeners to all markdown elements
    document.querySelectorAll('.stMarkdown').forEach(element => {
        element.addEventListener('mousedown', handleDragStart);
        element.addEventListener('mousemove', handleDrag);
        element.addEventListener('mouseup', handleDragEnd);
        element.addEventListener('mouseleave', handleDragEnd);
    });
    </script>
    """

    # Create the component with the JavaScript code
    components.html(js_code, height=0)

    # Create a hidden text input to capture the selected text
    selected_text = st.text_area("", value="", key="text_selection_input", label_visibility="collapsed")

    # Update session state with the selected text
    if selected_text:
        st.session_state.selected_text = selected_text

    # Display the selected text if it exists
    if st.session_state.selected_text:
        st.write("Selected text:", st.session_state.selected_text)
