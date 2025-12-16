<!DOCTYPE html>
<html>
<head>
    <title>Latest Evaluation Result</title>
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
            padding: 20px;
            margin: 20px 0;
            background-color: #f9f9f9;
        }
        .expr {
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .result {
            color: #0066cc;
            font-size: 1.2em;
        }
        .no-result {
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
    </style>
</head>
<body>
    <h1>Latest Evaluation Result</h1>
    % if latest:
    <div class="result-box">
        <div class="expr">Expression: <code>{{latest['expr']}}</code></div>
        <div class="result">Result: <code>{{latest['result']}}</code></div>
    </div>
    % else:
    <div class="no-result">No evaluation results yet.</div>
    % end
    <p><a href="/result">View all results</a></p>
</body>
</html>

