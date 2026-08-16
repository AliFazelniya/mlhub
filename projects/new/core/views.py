from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .llm_service import generate_answer
from django.shortcuts import render

class AskQuestionView(APIView):
    def post(self, request):
        question = request.data.get('question')
        if not question:
            return Response({"error": "Please provide a question."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = generate_answer(question)
            return Response({
                "question": question,
                "answer": result["answer"],
                "sources": result["sources"]
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def chat_interface(request):
    return render(request, 'chat.html')