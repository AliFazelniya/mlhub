"""HTTP views for the Hybrid RAG application."""

from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey

from .llm_service import generate_answer


class AskQuestionView(APIView):
    """Serve API-key-protected RAG question requests."""

    permission_classes = [HasAPIKey]

    def post(self, request):
        """Generate an answer for a submitted question.

        Args:
            request: The DRF request containing a question value.

        Returns:
            A DRF response containing the answer and source documents.
        """
        question = request.data.get("question")
        if not question:
            return Response(
                {"error": "Please provide a question."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = generate_answer(question)
            return Response(
                {
                    "question": question,
                    "answer": result["answer"],
                    "sources": result["sources"],
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def chat_interface(request):
    """Render the browser chat interface.

    Args:
        request: The incoming Django HTTP request.

    Returns:
        The rendered chat page response.
    """
    return render(request, "chat.html")
