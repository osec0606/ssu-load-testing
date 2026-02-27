document.getElementById('loadTestForm').addEventListener('submit', function(e) {
    e.preventDefault();

    
    const url = document.querySelector('input[name="url"]').value;
    const num_requests = document.querySelector('input[name="num_requests"]').value;
    function extractURLFromSummary(summary) {
        
        const urlRegex = /(https?:\/\/[^\s]+)/;
        
        const match = summary.match(urlRegex);
        if (match && match[0]) {
            
            return match[0];
        } else {
            
            return "No URL found";
        }
      }
    loadingSplash("add");

    fetch('/load-test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            url: url,
            num_requests: parseInt(num_requests, 10)
        }),
    })
    .then(response => response.json())
    .then(data => {
        loadingSplash("remove");
        displayDot("loadTest");
        console.log(data)
        document.getElementById('averageResponseTime').textContent = data.average_response_time.toFixed(3);
        document.getElementById('numRequestsHigherThanAverage').textContent = data.number_of_requests_higher_than_average;
        document.getElementById('successPercentage').textContent = data.success_percentage.toFixed(2);
        document.getElementById('message').textContent = data.summary_message;
        const firstLine = extractURLFromSummary(data.summary_message);
        
        const newTableContainer = document.createElement('div');
        newTableContainer.innerHTML = `
                    <div class="pageHeader">${firstLine}</div>
                    <table id="newMyTable" class="dataTable-table"></table>
            `;
        const oldTable = document.querySelector('#myTable');
        
        
        if (oldTable) {
            oldTable.parentNode.replaceChild(newTableContainer, oldTable);
        } else {
            
            console.error('#myTable element not found.');
            return;
        }
        
        
        var resultsForTable = data.details_of_requests_higher_than_average;
        if (resultsForTable && resultsForTable.length > 0) {
            
            window.dataTable = new simpleDatatables.DataTable("#newMyTable", {
              data: {
                headings: ["Request Number", "Status Code", "Response Time"],
                data: resultsForTable.map(function(item) {
                  return [item["Request Number"], item["Status Code"], item["Response Time"]];
                })
              },
            });
        } else {
            console.error('No data available to populate the table.');
        }

        


    })
    .catch((error) => {
        console.error('Error:', error);
    });
});
