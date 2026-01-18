document.addEventListener('click', async (event) => {
  if (event.target.classList.contains('delete-btn')) {
    const participant = event.target.getAttribute('data-participant');
    const activityName = event.target.getAttribute('data-activity');
    
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(participant)}`,
        {
          method: "POST",
        }
      );

      if (response.ok) {
        // Refresh activities list after deletion
        const activitiesList = document.getElementById("activities-list");
        // Clear the list and reload
        const event = new Event('refresh-activities');
        document.dispatchEvent(event);
        location.reload(); // Simple reload to refresh the activities
      } else {
        const result = await response.json();
        alert("Failed to unregister: " + (result.detail || "Unknown error"));
      }
    } catch (error) {
      console.error("Error unregistering participant:", error);
      alert("Failed to unregister participant");
    }
  }
});