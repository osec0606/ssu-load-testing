function extractURLFromSummary(summary) {
  
  const urlRegex = /(https?:\/\/[^\s]+)/;
  
  const match = summary.match(urlRegex);
  if (match && match[0]) {
      
      return match[0];
  } else {
      
      return "No URL found";
  }
}

document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("requestsForm")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      loadingSplash("add");
      const url = document.getElementById("url").value;
      const num_users = document.getElementById("num_users").value;
      const num_requests_per_user = document.getElementById(
        "num_requests_per_user"
      ).value;

      fetch("/send_requests", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: url,
          num_users: parseInt(num_users, 10),
          num_requests_per_user: parseInt(num_requests_per_user, 10),
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          loadingSplash("remove");
          displayDot("multiScenarioTest");
          console.log(data)
          const tableContainer = document.getElementById("tablesContainer");
          tableContainer.innerHTML = ""; 

          
          const summaryDiv = document.createElement("div");
          summaryDiv.className = "summary";
          summaryDiv.innerHTML = `<h2>Summary</h2>${data.summary_message.replace(
            /\n/g,
            "<br>"
          )}`;
          tableContainer.appendChild(summaryDiv);

          
          if (!Array.isArray(data.results)) {
            console.error("Results is not an array:", data.results);
            return;
          }

          
          const groupedResults = data.results.reduce((acc, cur) => {
            (acc[cur.user_id] = acc[cur.user_id] || []).push(cur);
            return acc;
          }, {});

          
          Object.entries(groupedResults).forEach(([userId, userResults]) => {
            const userResultsContainer = document.createElement("div");
            userResultsContainer.className = "user-results-container";

            const userTable = document.createElement("table");
            userTable.id = `userTable${userId}`;
            userTable.className = "dataTable-table";

            const theadHTML = `
                    <thead>
                        <tr>
                            <th>User ID</th>
                            <th>Request Number</th>
                            <th>Response Time (s)</th>
                        </tr>
                    </thead>
                `;
            userTable.innerHTML = theadHTML;

            const tbody = document.createElement("tbody");
            userResults.forEach((request, index) => {
              const row = tbody.insertRow();
              row.insertCell(0).textContent = userId;
              row.insertCell(1).textContent = index + 1; 
              row.insertCell(2).textContent = request.response_time.toFixed(3);
            });

            userTable.appendChild(tbody);
            userResultsContainer.appendChild(userTable);
            tableContainer.appendChild(userResultsContainer);
          });
        })
        .catch((error) => {
          console.error("Fetch error:", error);
          alert("An error occurred while fetching data.");
        });
    });

  const form = document.getElementById("requestsForm");

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(form);

    fetch("/k6-load-test", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.text())
      .then((data) => {
        
        document.body.innerHTML = data;
      })
      .catch((error) => {
        console.error("Error:", error);
        
      });
  });
});
