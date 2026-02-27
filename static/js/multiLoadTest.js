let urls = []; 

function addUrlInput() {
  const input = document.querySelector(
    "#urlInputsContainer .inputDiv:last-child input"
  );
  if (input.value.trim() !== "") {
    urls.push(input.value.trim()); 
    alert("URL added: " + input.value.trim()); 
    input.value = ""; 
  } else {
    alert("Please enter a URL.");
  }
}

function extractURLFromSummary(summary) {
  
  const urlRegex = /(https?:\/\/[^\s]+)/;
  
  const match = summary.match(urlRegex);
  if (match && match[0]) {
      
      return match[0];
  } else {
      
      return "No URL found";
  }
}

document
  .getElementById("multiLoadTestForm")
  .addEventListener("submit", function (e) {
    e.preventDefault();
    loadingSplash("add");
    const num_requests = document.getElementById("num_requests").value;
    const tablesContainer = document.getElementById("tablesContainer");

    fetch("/multi-load-test", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        urls: urls,
        num_requests: parseInt(num_requests, 10),
      }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        loadingSplash("remove");
        displayDot("multiLoadTest");
        
        tablesContainer.innerHTML = "";

        data.forEach((siteData, index) => {
          console.log(siteData);
          
          const newTableContainer = document.createElement("div");
          const firstLine = extractURLFromSummary(siteData.summary_message);
          console.log("selam")
          console.log(firstLine)

          newTableContainer.classList.add("formContent");
          newTableContainer.id = `tableContainer${index}`;
          newTableContainer.innerHTML = `
                <div class="pageHeader">${firstLine}</div>
                <div id="summary">
                    <p>Average Response Time: <span>${siteData.average_response_time.toFixed(
                      3
                    )}</span> seconds</p>
                    <p>Number of Requests Higher Than Average: <span>${
                      siteData.number_of_requests_higher_than_average
                    }</span></p>
                    <p>Success Percentage: <span>${siteData.success_percentage.toFixed(
                      2
                    )}</span>%</p>
                    <p>Message: <span>${siteData.summary_message}</span></p>
                    </div>
                </div>
                <table id="myTable${index}" class="dataTable-table"></table>
            `;
          tablesContainer.appendChild(newTableContainer);

          
          var resultsForTable =
            siteData.details_of_requests_higher_than_average;
          if (resultsForTable && resultsForTable.length > 0) {
            new simpleDatatables.DataTable(`#myTable${index}`, {
              data: {
                headings: ["Request Number", "Status Code", "Response Time"],
                data: resultsForTable.map((item) => [
                  item["Request Number"],
                  item["Status Code"],
                  item["Response Time"],
                ]),
              },
            });
          } else {
            console.error("No data available to populate the table.");
          }
        });
      })
      .catch((error) => {
        console.error("Error:", error);
      });

    urls = []; 
  });


document.querySelector(".addUrlButton").addEventListener("click", addUrlInput);