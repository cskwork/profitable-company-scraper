$(document).ready(function() {
    const api = new API();
    const searchInput = $('#companySearch');
    const searchResults = $('#searchResults');
    const loadingSpinner = $('.loading-spinner');
    let currentLanguage = CONFIG.DEFAULT_LANGUAGE;
    let currentSymbol = '';
    let chartData = null;

    function showLoading() {
        loadingSpinner.show();
    }

    function hideLoading() {
        loadingSpinner.hide();
    }

    $('#language-select').change(function() {
        currentLanguage = $(this).val();
        if (currentSymbol) {
            analyzeCompany(currentSymbol);
        }
    });

    function displayCompanyInfo(data) {
        chartData = data.stock_history;

        $('#companyDescription').text(data.company_data['Company Description']);
        
        $('#profitMargin').text(data.company_data['Profit Margin']);
        $('#peRatio').text(data.company_data['Trailing P/E'] === 'N/A' ? 'N/A' : parseFloat(data.company_data['Trailing P/E']).toFixed(2));
        $('#marketCap').text(data.company_data['Market Cap']);
        $('#revenueGrowth').text(data.company_data['Quarterly Revenue Growth  (yoy)']);

        $('#overallSummary').text(data.summary);
        
        const insightsList = $('#insights');
        insightsList.empty();
        if (data.summary.insights) {
            data.summary.insights.forEach(insight => {
                insightsList.append(`<li class="list-group-item">${insight}</li>`);
            });
        }

        if (chartData && chartData.length > 0) {
            const dates = chartData.map(item => item.Date);
            const prices = chartData.map(item => item.Close);

            const trace = {
                x: dates,
                y: prices,
                type: 'scatter',
                mode: 'lines',
                name: data.company_data.name || currentSymbol
            };

            const translations = CONFIG.TRANSLATIONS[currentLanguage];
            const layout = {
                title: {
                    text: `${data.company_data.name || currentSymbol} ${translations.CHART_TITLE}`,
                    font: { size: 18 }
                },
                xaxis: { 
                    title: translations.DATE_LABEL,
                    tickformat: '%Y-%m-%d'
                },
                yaxis: { 
                    title: translations.PRICE_LABEL,
                    tickprefix: '$'
                },
                hovermode: 'x unified',
                showlegend: true
            };

            Plotly.newPlot('stockChart', [trace], layout, CONFIG.CHART_CONFIG);
        } else {
            const translations = CONFIG.TRANSLATIONS[currentLanguage];
            $('#stockChart').html(`<div class="alert alert-warning">${translations.NO_DATA}</div>`);
        }

        const translations = CONFIG.TRANSLATIONS[currentLanguage];
        let tableHtml = '<table class="table table-striped">';
        tableHtml += `<thead><tr><th>${translations.METRIC_LABEL}</th><th>${translations.VALUE_LABEL}</th></tr></thead><tbody>`;
        
        Object.entries(data.company_data).forEach(([key, value]) => {
            if (key !== 'Company Description') {
                tableHtml += `<tr><td>${key}</td><td>${value}</td></tr>`;
            }
        });
        
        tableHtml += '</tbody></table>';
        $('#financialDetails').html(tableHtml);
    }

    async function analyzeCompany(symbol) {
        if (!symbol) return;

        showLoading();
        $('#analysisContainer').hide();
        $('#company-info').empty();

        try {
            const data = await api.analyzeCompany(symbol, currentLanguage);
            if (data.error) {
                const translations = CONFIG.TRANSLATIONS[currentLanguage];
                $('#company-info').html(`<div class="alert alert-danger">${data.error}</div>`);
                hideLoading();
                return;
            }

            $('#analysisContainer').show();
            displayCompanyInfo(data);
        } catch (error) {
            const translations = CONFIG.TRANSLATIONS[currentLanguage];
            $('#company-info').html(`<div class="alert alert-danger">${translations.ERROR}: ${error.message}</div>`);
        } finally {
            hideLoading();
        }
    }

    searchInput.on('input', async function() {
        const query = $(this).val().trim();
        
        if (query.length < 2) {
            searchResults.hide();
            return;
        }

        try {
            const results = await api.searchCompany(query, currentLanguage);
            
            if (results.length > 0) {
                searchResults.empty();
                results.forEach(result => {
                    const resultItem = $('<div>')
                        .addClass('search-result-item')
                        .text(`${result.name} (${result.symbol})`)
                        .click(function() {
                            currentSymbol = result.symbol;
                            searchInput.val(`${result.name} (${result.symbol})`);
                            searchResults.hide();
                            analyzeCompany(result.symbol);
                        });
                    searchResults.append(resultItem);
                });
                searchResults.show();
            } else {
                searchResults.hide();
            }
        } catch (error) {
            console.error('Search error:', error);
            searchResults.hide();
        }
    });

    $(document).click(function(event) {
        if (!$(event.target).closest('.search-results, #companySearch').length) {
            searchResults.hide();
        }
    });
});
