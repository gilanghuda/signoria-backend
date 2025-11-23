# Frontend Quiz Integration Guide

## 🔐 Authentication (JWT from Cookies)

All quiz endpoints automatically use your JWT token. **No manual token passing needed!**

### How It Works
1. After login, token is stored in HTTP-only cookies
2. Browser automatically sends cookies with every request
3. Server extracts token from cookie/Authorization header
4. You get authenticated automatically

### JavaScript Example
```javascript
// No need to do anything special!
// Just make normal fetch requests

const response = await fetch('http://localhost:8000/api/quizzes');
// Token is automatically sent in cookies!
```

---

## 📱 Quiz Flow Diagram

```
┌─────────────────────────────────────────────────┐
│ 1. GET /api/quizzes                             │
│    (List all quizzes)                           │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ 2. GET /api/quizzes/{quiz_id}                   │
│    (Get quiz with all questions & options)      │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ 3. POST /api/quizzes/{quiz_id}/attempts         │
│    (Start attempt, get attempt_id)              │
│    ⚠️ SAVE attempt_id! Needed for next steps   │
└────────────┬────────────────────────────────────┘
             │
             ▼
    ┌────────────────────┐
    │ Loop each question │
    └────────────┬───────┘
                 │
      ┌──────────┴──────────┐
      │                     │
      ▼                     ▼
  Text/Image          Camera Based
  Question            Question
      │                     │
      ▼                     ▼
  POST /answers      POST /camera-answers
      │                     │
      └──────────┬──────────┘
                 │
      (Repeat for all questions)
                 │
                 ▼
    ┌─────────────────────────────────┐
    │ POST /submit                    │
    │ (Calculate final score)         │
    │ ⚠️ NO MORE ANSWERS AFTER THIS  │
    └────────────┬────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────┐
    │ GET /result                     │
    │ (Show detailed feedback)        │
    └─────────────────────────────────┘
```

---

## 🚀 Step-by-Step Implementation

### Step 1: Get Quizzes

```javascript
async function getQuizzes() {
  try {
    const response = await fetch(
      'http://localhost:8000/api/quizzes?skip=0&limit=10'
    );
    
    if (!response.ok) throw new Error('Failed to fetch quizzes');
    
    const data = await response.json();
    console.log('Available quizzes:', data.data);
    return data.data;
    
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Step 2: Get Quiz Details

```javascript
async function getQuizDetails(quizId) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/quizzes/${quizId}`
    );
    
    if (!response.ok) throw new Error('Failed to fetch quiz');
    
    const data = await response.json();
    const quiz = data.data;
    
    console.log('Quiz title:', quiz.title);
    console.log('Total questions:', quiz.total_questions);
    console.log('Questions:', quiz.questions);
    
    return quiz;
    
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Step 3: Start Quiz Attempt

```javascript
async function startQuizAttempt(quizId) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/quizzes/${quizId}/attempts`,
      {
        method: 'POST'
        // Token is in cookies, no need to pass manually!
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      console.error('Error:', error);
      throw new Error('Failed to start attempt');
    }
    
    const data = await response.json();
    const attemptId = data.data.attempt_id;
    
    console.log('Attempt started!');
    console.log('Attempt ID:', attemptId);
    console.log('Total questions:', data.data.total_questions);
    
    // ⚠️ SAVE attempt_id! You'll need it for all answer submissions
    localStorage.setItem('currentAttemptId', attemptId);
    
    return attemptId;
    
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Step 4: Submit Answer (Text/Image Options)

```javascript
async function submitAnswer(quizId, attemptId, questionId, selectedOptionId) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/quizzes/${quizId}/attempts/${attemptId}/answers`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question_id: questionId,
          selected_option_id: selectedOptionId
        })
      }
    );
    
    if (!response.ok) throw new Error('Failed to submit answer');
    
    const data = await response.json();
    const isCorrect = data.data.is_correct;
    
    // ✅ Show immediate feedback to user
    if (isCorrect) {
      console.log('✓ Correct!');
      // Show green check, play success sound, etc.
    } else {
      console.log('✗ Wrong!');
      // Show red X, play error sound, etc.
    }
    
    return data.data;
    
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Step 5: Submit Camera Answer

```javascript
async function submitCameraAnswer(quizId, attemptId, questionId, mlPrediction) {
  // mlPrediction should be true/false from your ML model
  
  try {
    const response = await fetch(
      `http://localhost:8000/api/quizzes/${quizId}/attempts/${attemptId}/camera-answers`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question_id: questionId,
          is_correct: mlPrediction  // From your gesture recognition model
        })
      }
    );
    
    if (!response.ok) throw new Error('Failed to submit camera answer');
    
    const data = await response.json();
    
    console.log('Camera answer submitted');
    console.log('ML Prediction was correct:', data.data.is_correct);
    
    return data.data;
    
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Step 6: Submit Quiz (IMPORTANT!)

```javascript
async function submitQuiz(quizId, attemptId) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/quizzes/${quizId}/attempts/${attemptId}/submit`,
      {
        method: 'POST'
      }
    );
    
    if (!response.ok) throw new Error('Failed to submit quiz');
    
    const data = await response.json();
    const result = data.data;
    
    // ⚠️ This is the official score from server
    console.log('Quiz submitted!');
    console.log('Final score:', result.score);
    console.log('Total questions:', result.total_questions);
    console.log('Percentage:', result.percentage + '%');
    
    return result;
    
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Step 7: Show Results

```javascript
async function showResults(quizId, attemptId) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/quizzes/${quizId}/attempts/${attemptId}/result`
    );
    
    if (!response.ok) throw new Error('Failed to fetch results');
    
    const data = await response.json();
    const results = data.data;
    
    console.log('Final Score:', results.score + '/' + results.total_questions);
    console.log('Percentage:', results.percentage + '%');
    
    // Show detailed feedback
    results.answers.forEach((answer, index) => {
      console.log(`\nQuestion ${index + 1}:`);
      console.log('Category:', answer.question_category);
      console.log('Your answer:', answer.selected_option_content);
      console.log('Correct:', answer.is_correct ? '✓' : '✗');
      console.log('Explanation:', answer.explanation);
    });
    
    return results;
    
  } catch (error) {
    console.error('Error:', error);
  }
}
```

---

## 📋 Complete Example Flow

```javascript
async function runQuiz(quizId) {
  console.log('Starting quiz...');
  
  // 1. Get quiz details
  const quiz = await getQuizDetails(quizId);
  if (!quiz) return;
  
  // 2. Start attempt
  const attemptId = await startQuizAttempt(quizId);
  if (!attemptId) return;
  
  // 3. Loop through questions
  for (const question of quiz.questions) {
    console.log(`\n📋 Question: ${question.question_text}`);
    
    if (question.question_category === 'camera_based') {
      // Camera-based question
      console.log('Activate camera for gesture recognition...');
      
      // Your ML model inference here
      const mlPrediction = await runMLModel(question.question_text);
      
      await submitCameraAnswer(quizId, attemptId, question.id, mlPrediction);
      
    } else {
      // Text/Image question
      console.log('Options:');
      question.options.forEach((opt, idx) => {
        console.log(`  ${idx + 1}. ${opt.content}`);
      });
      
      // User selects option
      const userSelectedOptionId = question.options[0].id; // Example
      
      await submitAnswer(quizId, attemptId, question.id, userSelectedOptionId);
    }
  }
  
  // 4. Submit quiz (calculate score)
  const finalResult = await submitQuiz(quizId, attemptId);
  console.log(`\n🎯 Final Score: ${finalResult.percentage}%`);
  
  // 5. Show detailed results
  const results = await showResults(quizId, attemptId);
  
  return results;
}
```

---

## ⚠️ Common Mistakes & Fixes

### ❌ Mistake 1: Forgetting to save attempt_id

```javascript
// WRONG ❌
const response = await fetch(`/api/quizzes/${quizId}/attempts`, {method: 'POST'});
// ... forget to save attempt_id
// Later: attemptId is undefined!

// CORRECT ✅
const response = await fetch(`/api/quizzes/${quizId}/attempts`, {method: 'POST'});
const attemptId = (await response.json()).data.attempt_id;
localStorage.setItem('currentAttemptId', attemptId); // Save it!
```

### ❌ Mistake 2: Using is_correct from submit answer to calculate score

```javascript
// WRONG ❌
let totalScore = 0;
for (const answer of allAnswers) {
  const response = await submitAnswer(...);
  if (response.is_correct) totalScore++;
}
// This is NOT the official score!

// CORRECT ✅
// Submit all answers, then:
const finalResult = await submitQuiz(quizId, attemptId);
const officialScore = finalResult.score; // Use this!
```

### ❌ Mistake 3: Not passing question_id correctly

```javascript
// WRONG ❌
const response = await fetch(`/answers`, {
  body: JSON.stringify({
    // Missing question_id!
    selected_option_id: optionId
  })
});

// CORRECT ✅
const response = await fetch(`/answers`, {
  body: JSON.stringify({
    question_id: questionId,        // Include this!
    selected_option_id: optionId
  })
});
```

### ❌ Mistake 4: Calling submit endpoint twice

```javascript
// WRONG ❌
await submitQuiz(quizId, attemptId); // First call
await submitQuiz(quizId, attemptId); // Second call - ERROR!

// CORRECT ✅
const result = await submitQuiz(quizId, attemptId); // Call only once
```

---

## 🔗 Image URLs

Images are served from the static server:

```
https://signoria.gilanghuda.my.id/dict/dictionary/{CHARACTER}.jpg
```

**Available characters:**
- **Letters:** A, B, C, D, E, F, G, H, I, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y
- **Numbers:** 0, 1, 2, 3, 4, 5, 6, 7, 8, 9

**Examples:**
```
https://signoria.gilanghuda.my.id/dict/dictionary/A.jpg
https://signoria.gilanghuda.my.id/dict/dictionary/5.jpg
```

---

## 🧪 Testing with cURL

```bash
# Get quizzes
curl http://localhost:8000/api/quizzes?skip=0&limit=10

# Get quiz details
curl http://localhost:8000/api/quizzes/{quiz_id}

# Start attempt (requires authentication)
curl -X POST http://localhost:8000/api/quizzes/{quiz_id}/attempts \
  -H "Authorization: Bearer {your_token}"

# Submit answer
curl -X POST http://localhost:8000/api/quizzes/{quiz_id}/attempts/{attempt_id}/answers \
  -H "Content-Type: application/json" \
  -d '{"question_id":"...","selected_option_id":"..."}'

# Submit camera answer
curl -X POST http://localhost:8000/api/quizzes/{quiz_id}/attempts/{attempt_id}/camera-answers \
  -H "Content-Type: application/json" \
  -d '{"question_id":"...","is_correct":true}'

# Submit quiz
curl -X POST http://localhost:8000/api/quizzes/{quiz_id}/attempts/{attempt_id}/submit

# Get results
curl http://localhost:8000/api/quizzes/{quiz_id}/attempts/{attempt_id}/result
```

---

## 🛠️ Error Handling

```javascript
async function handleQuizError(response) {
  if (!response.ok) {
    const error = await response.json();
    
    if (response.status === 401) {
      console.error('Not authenticated. Please login first.');
      // Redirect to login
    } else if (response.status === 404) {
      console.error('Quiz or attempt not found.');
    } else if (response.status === 422) {
      console.error('Invalid request data:', error.detail);
    } else {
      console.error('Server error:', error);
    }
  }
}
```

---

## 📚 Response Structure

All quiz endpoints return this structure:

```json
{
  "status": "success",
  "data": {
    // endpoint-specific data here
  }
}
```

Error responses:
```json
{
  "detail": "Error message here"
}
```

---

## 💡 Tips

1. **Save attempt_id immediately** after starting a quiz
2. **Show question_category** to determine UI (image vs camera)
3. **Use is_correct from answers** only for immediate UI feedback
4. **Use score from submit endpoint** as official score
5. **Images are full URLs**, not paths - display directly
6. **Token is automatic**, no manual passing needed
7. **No answer submissions after submit** - endpoint is locked

You're ready to implement! 🚀
