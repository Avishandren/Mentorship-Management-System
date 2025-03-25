function submitReview() {
    const form = document.getElementById('reviewForm');
    const studentId = form.student_id.value;
    const category = form.category.value;
    const referenceId = form.reference_id.value;
    const rating = form.rating.value;
    const comment = form.comment.value;

    const reviewData = {
        student_id: studentId,
        category: category,
        reference_id: referenceId,
        rating: parseInt(rating),
        comment: comment
    };

    fetch('/submit_review', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(reviewData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message); // Success message
        } else if (data.error) {
            alert(data.error); // Error message
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred.');
    });
}