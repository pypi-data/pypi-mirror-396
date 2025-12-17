"""
PyX Charts Component
Native chart components using Chart.js.
"""
from ..ui import UI, Element
import json


class Chart:
    """
    PyX Chart Component using Chart.js.
    
    Supported chart types:
    - line: Line chart
    - bar: Bar chart
    - pie: Pie chart
    - doughnut: Doughnut chart
    - area: Area chart (line with fill)
    - radar: Radar/Spider chart
    - candlestick: Candlestick chart (for trading)
    """
    
    # Chart.js CDN
    CDN_SCRIPT = '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
    
    @staticmethod
    def _generate_id():
        """Generate unique chart ID"""
        import random
        return f"pyx-chart-{random.randint(10000, 99999)}"
    
    @staticmethod
    def line(
        labels: list,
        datasets: list,
        title: str = None,
        width: str = "100%",
        height: str = "300px"
    ) -> Element:
        """
        Create a Line Chart.
        
        Args:
            labels: X-axis labels ["Jan", "Feb", "Mar"]
            datasets: List of dataset dicts [{"label": "Sales", "data": [10, 20, 30], "color": "blue"}]
            title: Chart title
            width: Chart width
            height: Chart height
            
        Usage:
            Chart.line(
                labels=["Jan", "Feb", "Mar"],
                datasets=[
                    {"label": "Revenue", "data": [100, 200, 150], "color": "#3b82f6"},
                    {"label": "Expenses", "data": [80, 120, 100], "color": "#ef4444"}
                ],
                title="Monthly Report"
            )
        """
        return Chart._create_chart("line", labels, datasets, title, width, height)
    
    @staticmethod
    def bar(
        labels: list,
        datasets: list,
        title: str = None,
        width: str = "100%",
        height: str = "300px"
    ) -> Element:
        """Create a Bar Chart."""
        return Chart._create_chart("bar", labels, datasets, title, width, height)
    
    @staticmethod
    def pie(
        labels: list,
        data: list,
        colors: list = None,
        title: str = None,
        width: str = "300px",
        height: str = "300px"
    ) -> Element:
        """
        Create a Pie Chart.
        
        Usage:
            Chart.pie(
                labels=["Apple", "Banana", "Orange"],
                data=[30, 50, 20],
                colors=["#ef4444", "#eab308", "#f97316"]
            )
        """
        if not colors:
            colors = Chart._default_colors(len(data))
        
        datasets = [{"data": data, "backgroundColor": colors}]
        return Chart._create_chart("pie", labels, datasets, title, width, height, is_pie=True)
    
    @staticmethod
    def doughnut(
        labels: list,
        data: list,
        colors: list = None,
        title: str = None,
        width: str = "300px",
        height: str = "300px"
    ) -> Element:
        """Create a Doughnut Chart."""
        if not colors:
            colors = Chart._default_colors(len(data))
        
        datasets = [{"data": data, "backgroundColor": colors}]
        return Chart._create_chart("doughnut", labels, datasets, title, width, height, is_pie=True)
    
    @staticmethod
    def area(
        labels: list,
        datasets: list,
        title: str = None,
        width: str = "100%",
        height: str = "300px"
    ) -> Element:
        """Create an Area Chart (Line with fill)."""
        # Add fill property to datasets
        for ds in datasets:
            ds["fill"] = True
        return Chart._create_chart("line", labels, datasets, title, width, height)
    
    @staticmethod
    def radar(
        labels: list,
        datasets: list,
        title: str = None,
        width: str = "400px",
        height: str = "400px"
    ) -> Element:
        """Create a Radar/Spider Chart."""
        return Chart._create_chart("radar", labels, datasets, title, width, height)
    
    @staticmethod
    def candlestick(
        data: list,
        title: str = None,
        width: str = "100%",
        height: str = "400px"
    ) -> Element:
        """
        Create a Candlestick Chart for trading.
        
        Args:
            data: List of OHLC dicts [{"date": "2024-01-01", "open": 100, "high": 110, "low": 95, "close": 105}]
            
        Note: Uses custom rendering since Chart.js doesn't natively support candlesticks.
        We'll use a simplified bar representation.
        """
        chart_id = Chart._generate_id()
        
        # Convert OHLC to simplified format
        labels = [d.get("date", d.get("x", "")) for d in data]
        
        # Create high-low range bars
        highs = [d.get("high", 0) for d in data]
        lows = [d.get("low", 0) for d in data]
        opens = [d.get("open", 0) for d in data]
        closes = [d.get("close", 0) for d in data]
        
        # Determine colors based on price movement
        colors = ["#22c55e" if c >= o else "#ef4444" for o, c in zip(opens, closes)]
        
        config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Price",
                    "data": closes,
                    "backgroundColor": colors,
                    "borderColor": colors,
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "title": {"display": bool(title), "text": title or ""},
                    "legend": {"display": False}
                },
                "scales": {
                    "y": {"beginAtZero": False}
                }
            }
        }
        
        return Chart._render_chart(chart_id, config, width, height)
    
    @staticmethod
    def _default_colors(count: int) -> list:
        """Generate default color palette"""
        palette = [
            "#3b82f6",  # Blue
            "#ef4444",  # Red
            "#22c55e",  # Green
            "#f59e0b",  # Amber
            "#8b5cf6",  # Purple
            "#ec4899",  # Pink
            "#06b6d4",  # Cyan
            "#f97316",  # Orange
        ]
        return (palette * ((count // len(palette)) + 1))[:count]
    
    @staticmethod
    def _create_chart(
        chart_type: str,
        labels: list,
        datasets: list,
        title: str,
        width: str,
        height: str,
        is_pie: bool = False
    ) -> Element:
        """Internal method to create chart configuration."""
        chart_id = Chart._generate_id()
        
        # Process datasets
        processed_datasets = []
        for i, ds in enumerate(datasets):
            if is_pie:
                processed_datasets.append(ds)
            else:
                color = ds.get("color", Chart._default_colors(len(datasets))[i])
                processed_datasets.append({
                    "label": ds.get("label", f"Dataset {i+1}"),
                    "data": ds.get("data", []),
                    "borderColor": color,
                    "backgroundColor": ds.get("fill", False) and f"{color}40" or color,
                    "fill": ds.get("fill", False),
                    "tension": 0.3
                })
        
        config = {
            "type": chart_type,
            "data": {
                "labels": labels,
                "datasets": processed_datasets
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "title": {
                        "display": bool(title),
                        "text": title or ""
                    }
                }
            }
        }
        
        return Chart._render_chart(chart_id, config, width, height)
    
    @staticmethod
    def _render_chart(chart_id: str, config: dict, width: str, height: str) -> Element:
        """Render chart as HTML element."""
        config_json = json.dumps(config)
        
        # Create canvas element with inline script
        html = f'''
        <div style="width: {width}; height: {height};">
            <canvas id="{chart_id}"></canvas>
        </div>
        <script>
            (function() {{
                const ctx = document.getElementById('{chart_id}');
                new Chart(ctx, {config_json});
            }})();
        </script>
        '''
        
        return UI.raw(html)


# Convenience alias
chart = Chart
