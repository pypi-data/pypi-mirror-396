import matplotlib.pyplot as plt
import plotly.graph_objects as go
import copy

def combine_plots(plot_list, labels=None, line_styles=None, colors=None,
                 swap_axes=False, show=True, grid=False,
                 xlim=None, ylim=None, title=None, xlabel=None, ylabel=None):
    """
    Combines multiple individual matplotlib Axes or plotly Figures into a single figure.
    
    Ensures all properties (color, linestyle, marker) are transferred from the source
    plots by default, only overriding if explicitly provided as arguments.
    
    Returns:
    - matplotlib Axes object OR plotly Figure object depending on input.
    """

    if not plot_list:
        raise ValueError("plot_list cannot be empty")

    first_plot = plot_list[0]
    
    # Define marker symbols for internal check (same list used in plot_2d)
    marker_symbols = ['o', 's', '^', 'x', '*', 'D', 'p', '+', 'v', '<', '>', '1', '2', '3', '4']

    # === MATPLOTLIB AXES HANDLING ===
    if hasattr(first_plot, 'lines'):
        fig, ax = plt.subplots()
        
        for i, plot_ax in enumerate(plot_list):
            first_line = True
            
            for line in plot_ax.lines:
                x, y = line.get_data()

                # --- 1. Retrieve Existing Properties (Default Transfer) ---
                current_color = line.get_color()
                current_marker = line.get_marker()
                current_linestyle = line.get_linestyle()
                current_markersize = line.get_markersize()
                current_linewidth = line.get_linewidth()
                
                # Normalize marker: Convert 'None' string to None
                if current_marker in ['None', '']:
                    current_marker = None
                    
                # Normalize linestyle: Matplotlib stores '' for marker-only plots
                if current_linestyle in ['None', '']: 
                    current_linestyle = 'None' 

                # --- 2. Apply Overrides from append_plots Arguments (Only for First Line) ---
                if first_line:
                    # Override Line Style / Marker
                    if line_styles and i < len(line_styles):
                        new_style = line_styles[i]
                        
                        if new_style in marker_symbols:
                            # Case A: User forces a marker (e.g., 'o', 'x')
                            current_marker = new_style
                            current_linestyle = 'None' # Ensure linestyle is off
                        else:
                            # Case B: User forces a line style (e.g., '--', 'solid')
                            current_linestyle = new_style
                            current_marker = None # Clear the marker

                    # Override Color
                    if colors and i < len(colors):
                        current_color = colors[i]
                
                # Apply label only to the first line of the current plot_ax
                label_to_use = labels[i] if first_line and labels and i < len(labels) else None

                # --- 3. Plot on the New Axes ---
                if swap_axes:
                    ax.plot(y, x, 
                            color=current_color, 
                            linestyle=current_linestyle if current_linestyle != 'None' else '', 
                            marker=current_marker if current_marker else '',
                            markersize=current_markersize,
                            linewidth=current_linewidth,
                            label=label_to_use)
                else:
                    ax.plot(x, y, 
                            color=current_color, 
                            linestyle=current_linestyle if current_linestyle != 'None' else '', 
                            marker=current_marker if current_marker else '',
                            markersize=current_markersize,
                            linewidth=current_linewidth,
                            label=label_to_use)

                first_line = False

        # --- 4. Final Axis/Figure Configuration (Matplotlib) ---
        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)
        if title:
            ax.set_title(title)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        if grid:
            ax.grid()
        if labels:
            ax.legend()
        if show:
            plt.show()
        else:
            plt.close()

        return ax

    # === PLOTLY FIGURE HANDLING ===
    elif hasattr(first_plot, 'data'):
        combined_fig = go.Figure()
        
        for i, fig in enumerate(plot_list):
            for trace in fig.data:
                # Use deepcopy for safe cloning of the trace
                new_trace = copy.deepcopy(trace)

                # Apply colors if provided and trace supports it
                if colors and i < len(colors):
                    if hasattr(new_trace, 'line'):
                        new_trace.line.color = colors[i]
                    if hasattr(new_trace, 'marker'):
                        new_trace.marker.color = colors[i]

                # Apply line styles (dash) if provided
                if line_styles and i < len(line_styles):
                    if isinstance(new_trace, go.Scatter) and hasattr(new_trace, 'line'):
                        new_trace.line.dash = line_styles[i]

                # Apply labels/name
                if labels and i < len(labels):
                    new_trace.name = labels[i]
                
                # Handle Axis Swap (if requested)
                if swap_axes and hasattr(new_trace, 'x') and hasattr(new_trace, 'y'):
                     new_trace.x, new_trace.y = new_trace.y, new_trace.x

                combined_fig.add_trace(new_trace)

        # Final Layout Configuration (Plotly)
        if title:
            combined_fig.update_layout(title=title)
        if xlabel or ylabel:
            combined_fig.update_layout(xaxis_title=xlabel if xlabel else None,
                                       yaxis_title=ylabel if ylabel else None)
        if xlim:
            combined_fig.update_xaxes(range=xlim)
        if ylim:
            combined_fig.update_yaxes(range=ylim)
        if grid:
            combined_fig.update_layout(xaxis_showgrid=True, yaxis_showgrid=True)

        if show:
            combined_fig.show()

        return combined_fig

    else:
        raise TypeError("Unknown plot object type passed to append_plots.")