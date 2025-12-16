<!DOCTYPE html>
<html>
<head>
    <title>All Evaluation Results</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .result-box {
            border: 1px solid #ddd;
            padding: 15px;
            margin: 15px 0;
            background-color: #f9f9f9;
        }
        .expr {
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }
        .result {
            color: #0066cc;
        }
        .no-results {
            color: #999;
            font-style: italic;
        }
        a {
            color: #0066cc;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .count {
            color: #666;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>All Evaluation Results</h1>
    % if results:
    <div class="count">Total results: {{len(results)}}</div>
    % for item in results:
    <div class="result-box">
        <div class="expr">Expression: <code>{{item['expr']}}</code></div>
        <div class="result">Result: <code>{{item['result']}}</code></div>
    </div>
    % end
    % else:
    <div class="no-results">No evaluation results yet.</div>
    % end
    <p><a href="/answer">View latest result</a></p>
</body>
</html>

