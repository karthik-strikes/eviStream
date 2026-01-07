# app/components/form_review_ui.py
"""
Simplified Form Review UI

Shows AI reasoning trace and approve/reject buttons.
No complex tabs or visualizations.
"""

import streamlit as st
from typing import Dict, Any
import json


def render_form_review_interface(
    project_id: str,
    form: Dict[str, Any],
    review_data: Dict[str, Any]
) -> None:
    """
    Simple form review interface - just reasoning and buttons.

    Args:
        project_id: Current project ID
        form: Form data
        review_data: Decomposition and validation data
    """
    form_id = form.get("id")
    form_name = form.get("form_name", "Untitled Form")

    st.markdown("---")
    st.markdown(f"### Review: {form_name}")

    # Status banner
    validation_results = review_data.get("validation_results") or {}
    if validation_results and validation_results.get("passed"):
        st.success(
            "Form decomposition is ready. The AI can start extracting information.")
    else:
        st.info("Review the AI's reasoning below and approve or request changes.")

    # Get reasoning trace from decomposition
    decomposition = review_data.get("decomposition") or {}
    reasoning = decomposition.get("reasoning_trace", "No reasoning available")

    # Show reasoning
    st.markdown("#### AI's Reasoning")
    st.markdown(
        "*See how the AI analyzed your form and decided to group fields:*")

    st.text_area(
        "AI Reasoning",
        value=reasoning,
        height=400,
        disabled=True,
        key=f"reasoning_display_{form_id}",
        label_visibility="collapsed"
    )

    # Quick stats
    signatures = decomposition.get("signatures") or []
    pipeline = decomposition.get("pipeline") or []

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Signatures Generated", len(signatures))
    with col2:
        st.metric("Pipeline Stages", len(pipeline))
    with col3:
        total_fields = sum(len(sig.get("fields", {})) for sig in signatures)
        st.metric("Fields Mapped", total_fields)

    # Action buttons
    st.markdown("---")
    st.markdown("### What would you like to do?")

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.button(
            "Approve and Generate Code",
            type="primary",
            use_container_width=True,
            key=f"approve_{form_id}"
        ):
            handle_approval(project_id, form, review_data)

    with col2:
        if st.button(
            "Request Changes",
            use_container_width=True,
            key=f"request_changes_{form_id}"
        ):
            st.session_state[f"show_feedback_{form_id}"] = True
            st.rerun()

    with col3:
        if st.button(
            "Cancel",
            use_container_width=True,
            key=f"cancel_{form_id}"
        ):
            st.info("Review cancelled. Form remains in current state.")
            st.rerun()

    # Show feedback form if requested
    if st.session_state.get(f"show_feedback_{form_id}"):
        show_feedback_form(project_id, form, review_data)


def show_feedback_form(project_id: str, form: Dict[str, Any], review_data: Dict[str, Any]):
    """Show simple feedback form inline."""
    form_id = form.get("id")

    st.markdown("---")
    st.markdown("#### What needs to change?")
    st.markdown("*Describe specific changes you want the AI to make:*")

    feedback = st.text_area(
        "Your feedback",
        height=150,
        key=f"feedback_input_{form_id}",
        placeholder="""Example feedback:

"Field X should be extracted AFTER Field Y because it depends on that information."

or

"Group medications and allergies together in the same extraction step."

Be as specific as possible to help the AI understand your requirements.""",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Submit Feedback", type="primary", key=f"submit_feedback_{form_id}"):
            if feedback and feedback.strip():
                handle_rejection(project_id, form, review_data, feedback)
            else:
                st.error("Please provide feedback before submitting")

    with col2:
        if st.button("Cancel", key=f"cancel_feedback_{form_id}"):
            st.session_state[f"show_feedback_{form_id}"] = False
            st.rerun()


def handle_approval(
    project_id: str,
    form: Dict[str, Any],
    review_data: Dict[str, Any]
) -> None:
    """
    Handle form approval - continue workflow to generate code.

    Args:
        project_id: Project ID
        form: Form data
        review_data: Review data with thread_id
    """
    from core.generators.form_review_bridge import get_decomposition_service

    form_id = form.get("id")
    thread_id = review_data.get("thread_id")

    if not thread_id:
        st.error("No thread ID found. Cannot continue workflow.")
        return

    with st.spinner("Generating DSPy code. This may take a minute."):
        service = get_decomposition_service()
        result = service.approve_decomposition(
            project_id=project_id,
            form_id=form_id,
            thread_id=thread_id
        )

    if result.get("success"):
        st.success("Form approved and code generated successfully.")
        st.balloons()

        # Show generation details
        with st.expander("Generation Details"):
            stats = result.get("result", {}).get("statistics", {})

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Signatures", stats.get("signatures_generated", 0))
            with col2:
                st.metric("Modules", stats.get("modules_generated", 0))
            with col3:
                st.metric("Pipeline Stages", stats.get("pipeline_stages", 0))

        st.info(
            "Form is now active. You can start uploading documents for extraction.")

        # Refresh page after a delay
        import time
        time.sleep(2)
        st.rerun()

    else:
        st.error(f"Code generation failed: {result.get('error')}")

        with st.expander("Show error details"):
            st.code(json.dumps(result, indent=2))


def handle_rejection(
    project_id: str,
    form: Dict[str, Any],
    review_data: Dict[str, Any],
    feedback: str
) -> None:
    """
    Handle form rejection - regenerate with feedback.

    Args:
        project_id: Project ID
        form: Form data
        review_data: Review data with thread_id
        feedback: User feedback
    """
    from core.generators.form_review_bridge import get_decomposition_service

    form_id = form.get("id")
    thread_id = review_data.get("thread_id")

    if not thread_id:
        st.error("No thread ID found. Cannot regenerate.")
        return

    with st.spinner("Regenerating form decomposition with your feedback..."):
        service = get_decomposition_service()
        result = service.reject_decomposition(
            project_id=project_id,
            form_id=form_id,
            thread_id=thread_id,
            feedback=feedback
        )

    if result.get("success"):
        if result.get("status") == "awaiting_review":
            st.success(
                "Form regenerated. Please review the updated decomposition.")
            st.info("The changes have been applied based on your feedback.")

            # Clear feedback form state
            if f"show_feedback_{form_id}" in st.session_state:
                del st.session_state[f"show_feedback_{form_id}"]

            import time
            time.sleep(2)
            st.rerun()

        elif result.get("status") == "completed":
            st.success("Form regenerated and approved automatically.")
            st.balloons()

            import time
            time.sleep(2)
            st.rerun()

    else:
        st.error(f"Regeneration failed: {result.get('error')}")


__all__ = ["render_form_review_interface"]
