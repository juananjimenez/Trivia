import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start= (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    question = [question.format() for question in selection]
    current_questions = question[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    setup_db(app)


    """
    @TODO (HECHO): Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    
    CORS(app, resources={r"/localhost/*": {"origins": "*"}})


    """
    @TODO (HECHO): Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true")
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
        return response
    
        
    @app.route('/')
    @app.route('/questions', methods=['GET'])
    def list_questions():

        questions= Question.query.order_by('id').all()
        all_questions = paginate_questions(request, questions)
       
        categories = Category.query.all()
        
        all_categories = {category.id: category.type for category in categories}

        return jsonify({
            'success': True,
            'total_questions': len(questions),
            'questions': all_questions,
            'current_category': all_categories,
            'categories': all_categories
            
        })

    """
    @TODO: (HECHO)
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/categories', methods=['GET'])
    def list_categories():
        categories = Category.query.all()
        
        all_categories = {category.id: category.type for category in categories}

        if categories is None:
            abort(400)
        else:

            return jsonify({
                'success': True,
                'categories': all_categories
            })


    """
    @TODO(HECHO):
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(400)
        else:
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })


    """
    @TODO: (HECHO)
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/add', methods=['POST'])
    def add_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        new_question = Question(
            question = new_question, 
            answer = new_answer, 
            category = new_category, 
            difficulty = new_difficulty)

        new_question.insert()

        return jsonify({
            'success': True,
        
            })
    

    """
    @TODO (HECHO):
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def search_word():
        
        body = request.get_json()
        searchTerm = body['searchTerm']
        questions = Question.query.filter(Question.question.ilike('%' + searchTerm + '%')).all()
       
        #create the questions from the db consult
        results = []
        for question in questions:
            results.append(
            {
                'question': question.question,
                'answer': question.answer,
                'difficulty': question.difficulty,
                'category': question.category
            }
            )
        
        return jsonify({
        'success': True,
        'questions':results,
        'totalQuestions': len(results),
        'current_category': results
        })


    """
    @TODO (HECHO):
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def question_by_category(category_id):

        try:

            search_category = Question.query.filter(Question.category == category_id).all()

            # create the results from the db search
            results = []
            for question in search_category:
                results.append(
                {
                    'question': question.question,
                    'answer': question.answer,
                    'difficulty': question.difficulty,
                    'category': question.category
                }
                )

            return jsonify({
            'success': True,
            'questions': results,
            'totalQuestions': len(results),
            'currentCategory': None
            })
        except:
            abort(400)


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/play', methods=['POST'])
    def question_play():
        body = request.get_json()
        quiz_category = body['quiz_category']['id']
        questions_category = Question.query.filter(Question.category == quiz_category)

        # create the questions from the selected category consult in the db
        questions=[]
        for question in questions_category:
            questions.append(question.format())

        print(questions)
        print(random.choice(questions))
        currentQuestion = random.choice(questions)
        print(currentQuestion['question'])
        print(currentQuestion['answer'])
        

        return jsonify({
            'success': True,
            'quizCategory': body['quiz_category'],
            'currentQuestion': currentQuestion,
            'previousQuestions': questions,
            
        })


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    # Errors in the app 

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': "Bad request"
        }) , 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "Not found"
        }), 404
    
    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': "Method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "Unprocessable"
        }), 422
    
    
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

