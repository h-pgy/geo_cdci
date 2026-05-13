import streamlit as st
import streamlit.components.v1 as components
import time

class AnchorManager:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        if "active_anchors" not in st.session_state:
            st.session_state.active_anchors = []

    @property
    def anchor_list(self) -> list[str]:
        return st.session_state.active_anchors

    def set_anchor(self, anchor_id):
        st.markdown(
            f'<div id="{anchor_id}" style="scroll-margin-top: 2em; height: 0px; margin: 0; padding: 0;"></div>',
            unsafe_allow_html=True
        )
        if anchor_id not in st.session_state.active_anchors:
            st.session_state.active_anchors.append(anchor_id)
            if self.verbose:
                print(f"Anchor '{anchor_id}' set at current position.")
    
    def anchor_exists(self, anchor_id) -> bool:
        return anchor_id in self.anchor_list

    def unset_anchor(self, anchor_id):
        if self.anchor_exists(anchor_id):
            st.session_state.active_anchors.remove(anchor_id)
            if self.verbose:
                print(f"Anchor '{anchor_id}' removed from active anchors.")

    def _execute_js(self, js_code):
        components.html(
            f"""
            <script>
                // Timestamp para forçar re-execução: {time.time()}
                (function() {{
                    {js_code}
                }})();
            </script>
            """,
            height=0,
            width=0,
        )

    def scroll_to(self, anchor_id):
        if self.anchor_exists(anchor_id):
            js = f"""
                function scrollToMySection() {{
                    var element = window.parent.document.getElementById("{anchor_id}");
                    if (element) {{
                        console.log("Elemento {anchor_id} encontrado. Scrollando...");
                        element.scrollIntoView({{ behavior: "smooth", block: "end" }});
                    }} else {{
                        console.log("Aguardando renderização de {anchor_id}...");
                        setTimeout(scrollToMySection, 100);
                    }}
                }}
                scrollToMySection();
            """
            self._execute_js(js)
            if self.verbose:
                print(f"Scrolled to anchor '{anchor_id}'.")

    def scroll_to_last_existing_anchor(self):
        for anchor_id in reversed(self.anchor_list):
            if self.anchor_exists(anchor_id):
                self.scroll_to(anchor_id)
                if self.verbose:
                    print('Scrolled to last existing anchor:', anchor_id)
                break