<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IT 인프라 표준화 통합 대시보드</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <style>
        :root {
            --bg: #0d0f14; --surface: #13161e; --surface2: #1a1e28;
            --border: #252a38; --text: #e2e6f0; --muted: #7a8099;
            --primary: #509ee3; --accent: #74b9f8; --red: #e05c5c; --green: #5ce08a;
        }
        body { font-family: 'Malgun Gothic', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; line-height: 1.6; }
        .container { max-width: 1300px; margin: auto; }
        
        /* 헤더 디자인 */
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 1px solid var(--border); padding-bottom: 15px; }
        .header h1 { font-size: 24px; color: var(--primary); margin: 0; }

        /* 업로드 섹션 */
        .upload-section { background: var(--surface); border: 2px dashed var(--primary); border-radius: 12px; padding: 40px; text-align: center; margin-bottom: 30px; cursor: pointer; transition: 0.3s; }
        .upload-section:hover { background: var(--surface2); border-color: var(--accent); }

        /* KPI 카드 */
        .kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .kpi-card { background: var(--surface); border: 1px solid var(--border); padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .kpi-label { color: var(--muted); font-size: 13px; margin-bottom: 10px; }
        .kpi-value { font-size: 28px; font-weight: bold; }

        /* 차트 영역 */
        .chart-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 20px; margin-bottom: 30px; }
        .chart-box { background: var(--surface); border: 1px solid var(--border); padding: 20px; border-radius: 12px; height: 320px; }

        /* 테이블 영역 */
        .table-box { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        th { background: var(--surface2); color: var(--primary); padding: 15px; font-size: 14px; border-bottom: 2px solid var(--border); }
        td { padding: 12px 15px; border-bottom: 1px solid var(--border); font-size: 13px; }
        tr:hover { background: rgba(80, 158, 227, 0.05); }
        .status-tag { padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>Dashboard <span style="font-weight: 300; color: white;">| IT Infra Standardization</span></h1>
        <div id="live-clock" style="color: var(--muted); font-family: monospace;"></div>
    </div>

    <div class="upload-section" onclick="document.getElementById('fileInput').click()">
        <p style="margin: 0; font-size: 16px;">📂 <b>인프라 자산 관리대장(Excel)</b>을 여기에 업로드하세요.</p>
        <span style="font-size: 12px; color: var(--muted);">파일명: IT_인프라_자산_버전표준화_관리대장.xlsx</span>
        <input type="file" id="fileInput" accept=".xlsx, .xls" style="display:none">
    </div>

    <div class="kpi-grid">
        <div class="kpi-card"><div class="kpi-label">전체 시스템 수</div><div class="kpi-value" id="totalCnt">-</div></div>
        <div class="kpi-card"><div class="kpi-label">업그레이드 필요</div><div class="kpi-value" id="upgradeCnt" style="color: var(--red);">-</div></div>
        <div class="kpi-card"><div class="kpi-label">정상(표준 준수)</div><div class="kpi-value" id="okCnt" style="color: var(--green);">-</div></div>
        <div class="kpi-card"><div class="kpi-label">전체 준수율</div><div class="kpi-value" id="rateCnt" style="color: var(--primary);">-</div></div>
    </div>

    <div class="chart-grid">
        <div class="chart-box"><canvas id="barChart"></canvas></div>
        <div class="chart-box"><canvas id="doughnutChart"></canvas></div>
    </div>

    <div class="table-box">
        <table id="assetTable">
            <thead>
                <tr>
                    <th>장비명(Hostname)</th>
                    <th>구분</th>
                    <th>현재 버전</th>
                    <th>권고 버전</th>
                    <th>상태</th>
                    <th>최종 업데이트</th>
                </tr>
            </thead>
            <tbody id="tableBody">
                <tr><td colspan="6" style="text-align:center; padding:50px; color:var(--muted);">데이터가 없습니다. 엑셀 파일을 업로드해주세요.</td></tr>
            </tbody>
        </table>
    </div>
</div>

<script>
    let charts = {};

    // 1. 엑셀 파일 읽기
    document.getElementById('fileInput').addEventListener('change', function(e) {
        const file = e.target.files[0];
        const reader = new FileReader();

        reader.onload = function(e) {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, {type: 'array'});
            const sheet = workbook.Sheets[workbook.SheetNames[0]]; // 첫 번째 시트 선택
            const json = XLSX.utils.sheet_to_json(sheet);
            renderDashboard(json);
        };
        reader.readAsArrayBuffer(file);
    });

    // 2. 대시보드 렌더링
    function renderDashboard(data) {
        const tbody = document.getElementById('tableBody');
        let upgradeCount = 0;
        let okCount = 0;
        const catStats = {};

        tbody.innerHTML = data.map(row => {
            // 엑셀 컬럼명 매핑 (업로드하신 파일의 실제 헤더 이름과 일치해야 합니다)
            const hostname = row['장비명(Hostname)'] || row['Hostname'] || '-';
            const category = row['장비 구분'] || row['구분'] || '기타';
            const curVer = String(row['OS/NOS 현재버전'] || row['현재버전'] || '');
            const stdVer = String(row['OS/NOS 권고버전'] || row['권고버전'] || '');
            const updateDate = row['최종 업데이트'] || '-';

            const isUpgrade = curVer !== stdVer;
            if(isUpgrade) upgradeCount++; else okCount++;
            catStats[category] = (catStats[category] || 0) + 1;

            return `
                <tr>
                    <td><b>${hostname}</b></td>
                    <td>${category}</td>
                    <td style="color:${isUpgrade ? 'var(--red)' : 'white'}">${curVer}</td>
                    <td style="color:var(--green)">${stdVer}</td>
                    <td><span class="status-tag" style="background:${isUpgrade ? 'rgba(224, 92, 92, 0.2)' : 'rgba(92, 224, 138, 0.2)'}; color:${isUpgrade ? 'var(--red)' : 'var(--green)'}">${isUpgrade ? '업그레이드 필요' : '정상'}</span></td>
                    <td style="color:var(--muted)">${updateDate}</td>
                </tr>
            `;
        }).join('');

        // KPI 업데이트
        document.getElementById('totalCnt').innerText = data.length;
        document.getElementById('upgradeCnt').innerText = upgradeCount;
        document.getElementById('okCnt').innerText = okCount;
        document.getElementById('rateCnt').innerText = Math.round((okCount/data.length)*100) + '%';

        updateCharts(catStats, upgradeCount, okCount);
    }

    // 3. 차트 업데이트
    function updateCharts(catData, upgrade, ok) {
        if(charts.bar) charts.bar.destroy();
        if(charts.pie) charts.pie.destroy();

        charts.bar = new Chart(document.getElementById('barChart'), {
            type: 'bar',
            data: {
                labels: Object.keys(catData),
                datasets: [{ label: '인프라 자산 분포', data: Object.values(catData), backgroundColor: '#509ee3' }]
            },
            options: { maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: '#252a38' } } } }
        });

        charts.pie = new Chart(document.getElementById('doughnutChart'), {
            type: 'doughnut',
            data: {
                labels: ['미준수', '정상'],
                datasets: [{ data: [upgrade, ok], backgroundColor: ['#e05c5c', '#5ce08a'], borderWidth: 0 }]
            },
            options: { maintainAspectRatio: false, cutout: '70%' }
        });
    }

    // 시계 기능
    setInterval(() => {
        document.getElementById('live-clock').innerText = new Date().toLocaleString();
    }, 1000);
</script>

</body>
</html>
