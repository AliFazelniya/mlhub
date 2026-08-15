from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .llm_service import generate_answer

class AskQuestionView(APIView):
    def post(self, request):
        question = request.data.get('question')
        
        if not question:
            return Response({"error": "لطفا یک سوال (question) ارسال کنید."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # فراخوانی تابعی که در llm_service ساختیم
            answer = generate_answer(question)
            return Response({"question": question, "answer": answer}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)