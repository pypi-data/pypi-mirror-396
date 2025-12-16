"""
Command-line interface for Itinerizer.
"""

import sys
import json
from pathlib import Path
from datetime import date, datetime
from uuid import UUID
import argparse

from . import ItineraryManager, __version__
from .config import get_config_manager, setup_local_storage
from .constants import (
    CLICommands, CLIArguments, ExportFormats, SegmentTypes, Messages,
    MarkdownTemplates, EncodingDefaults, BOOLEAN_TRUE_VALUES,
    INTEGER_CONFIG_KEYS, BOOLEAN_CONFIG_KEYS
)
from .models import Traveler


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="itinerizer",
        description="Itinerizer - Travel Itinerary Management System"
    )

    parser.add_argument(
        CLIArguments.VERSION,
        action="version",
        version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        CLIArguments.STORAGE_PATH,
        type=str,
        help="Custom storage path for itineraries",
        default=None
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser(CLICommands.LIST, help="List all itineraries")
    list_parser.add_argument(CLIArguments.STATUS, help="Filter by status")
    list_parser.add_argument(CLIArguments.TRIP_TYPE, help="Filter by trip type")

    # Get command
    get_parser = subparsers.add_parser(CLICommands.GET, help="Get an itinerary")
    get_parser.add_argument(CLIArguments.ID, type=str, help="Itinerary ID")
    get_parser.add_argument(CLIArguments.JSON, action="store_true", help="Output as JSON")

    # Create command
    create_parser = subparsers.add_parser(CLICommands.CREATE, help="Create an itinerary")
    create_parser.add_argument(CLIArguments.FILE, type=str, required=True, help="JSON file with itinerary data")

    # Delete command
    delete_parser = subparsers.add_parser(CLICommands.DELETE, help="Delete an itinerary")
    delete_parser.add_argument(CLIArguments.ID, type=str, help="Itinerary ID")

    # Validate command
    validate_parser = subparsers.add_parser(CLICommands.VALIDATE, help="Validate an itinerary file")
    validate_parser.add_argument("file", type=str, help="JSON file to validate")
    
    # Export command
    export_parser = subparsers.add_parser(CLICommands.EXPORT, help="Export an itinerary")
    export_parser.add_argument(CLIArguments.ID, type=str, help="Itinerary ID")
    export_parser.add_argument(CLIArguments.OUTPUT, type=str, required=True, help="Output file path")
    export_parser.add_argument(CLIArguments.FORMAT, type=str,
                              choices=[ExportFormats.JSON, ExportFormats.MARKDOWN],
                              default=ExportFormats.JSON,
                              help=f"Export format (default: {ExportFormats.JSON})")

    # Config command
    config_parser = subparsers.add_parser(CLICommands.CONFIG, help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="Config commands")

    # Config show
    config_subparsers.add_parser(CLICommands.CONFIG_SHOW, help="Show current configuration")

    # Config init
    init_parser = config_subparsers.add_parser(CLICommands.CONFIG_INIT, help="Initialize local configuration")
    init_parser.add_argument(CLIArguments.FORCE, action="store_true", help="Force reinitialize")

    # Config set
    set_parser = config_subparsers.add_parser(CLICommands.CONFIG_SET, help="Set configuration value")
    set_parser.add_argument(CLIArguments.KEY, help="Configuration key")
    set_parser.add_argument(CLIArguments.VALUE, help="Configuration value")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Initialize manager
    manager = ItineraryManager(storage_path=args.storage_path)
    
    try:
        if args.command == CLICommands.LIST:
            itineraries = manager.search_itineraries(
                status=args.status,
                trip_type=args.trip_type
            )

            if not itineraries:
                print(Messages.Info.NO_ITINERARIES)
            else:
                print(Messages.Info.ITINERARIES_FOUND.format(len(itineraries)))
                for itin in itineraries:
                    print(f"  - {itin.id}: {itin.title} ({itin.status})")
                    print(f"    {itin.start_date} to {itin.end_date}")
                    print(f"    Travelers: {len(itin.travelers)}, Segments: {len(itin.segments)}")
        
        elif args.command == CLICommands.GET:
            itinerary_id = UUID(args.id)
            itinerary = manager.get_itinerary(itinerary_id)

            if not itinerary:
                print(Messages.Error.ITINERARY_NOT_FOUND.format(args.id), file=sys.stderr)
                return 1
            
            if args.json:
                print(json.dumps(itinerary.model_dump(mode='json'), indent=2, default=str))
            else:
                print(f"Itinerary: {itinerary.title}")
                print(f"ID: {itinerary.id}")
                print(f"Status: {itinerary.status}")
                print(f"Dates: {itinerary.start_date} to {itinerary.end_date}")
                print(f"Travelers: {len(itinerary.travelers)}")
                print(f"Segments: {len(itinerary.segments)}")
                
                if itinerary.segments:
                    print("\nSegments:")
                    for seg in itinerary.segments:
                        print(f"  - {seg.type}: {seg.start_datetime.strftime('%Y-%m-%d %H:%M')}")
        
        elif args.command == CLICommands.CREATE:
            file_path = Path(args.file)
            if not file_path.exists():
                print(Messages.Error.FILE_NOT_FOUND.format(args.file), file=sys.stderr)
                return 1
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Parse dates
            if 'start_date' in data:
                data['start_date'] = date.fromisoformat(data['start_date'])
            if 'end_date' in data:
                data['end_date'] = date.fromisoformat(data['end_date'])
            
            # Parse travelers
            from .models import Traveler
            travelers = []
            for t_data in data.get('travelers', []):
                travelers.append(Traveler.model_validate(t_data))
            data['travelers'] = travelers
            
            itinerary = manager.create_itinerary(**data)
            print(Messages.Success.ITINERARY_CREATED.format(itinerary.id))

        elif args.command == CLICommands.DELETE:
            itinerary_id = UUID(args.id)
            if manager.delete_itinerary(itinerary_id):
                print(Messages.Success.ITINERARY_DELETED.format(args.id))
            else:
                print(Messages.Error.ITINERARY_NOT_FOUND.format(args.id), file=sys.stderr)
                return 1
        
        elif args.command == CLICommands.VALIDATE:
            file_path = Path(args.file)
            if not file_path.exists():
                print(Messages.Error.FILE_NOT_FOUND.format(args.file), file=sys.stderr)
                return 1
            
            with open(file_path) as f:
                data = json.load(f)
            
            from .models import Itinerary
            try:
                itinerary = Itinerary.model_validate(data)
                result = manager.validator.validate(itinerary)
                
                if result.is_valid:
                    print(Messages.Success.ITINERARY_VALID)
                else:
                    print(Messages.Error.ITINERARY_INVALID)
                    for error in result.errors:
                        print(f"  - {error.code}: {error.message}")

                if result.warnings:
                    print(Messages.Info.VALIDATION_WARNINGS)
                    for warning in result.warnings:
                        print(f"  - {warning.code}: {warning.message}")

            except Exception as e:
                print(Messages.Error.INVALID_FORMAT.format(e), file=sys.stderr)
                return 1
        
        elif args.command == CLICommands.CONFIG:
            config_manager = get_config_manager()

            if args.config_command == CLICommands.CONFIG_SHOW:
                config = config_manager.get_config()
                print(Messages.Info.CURRENT_CONFIG)
                print(f"  Storage Path: {config.storage_path}")
                print(f"  Backup Path: {config.backup_path}")
                print(f"  Web UI Port: {config.web_ui_port}")
                print(f"  API Port: {config.api_port}")
                print(f"  Log Level: {config.log_level}")
                print(f"  Auto Backup: {config.auto_backup}")
                print(f"  Backup Retention: {config.backup_retention_days} days")
                print(f"  Config File: {config_manager.config_file}")

            elif args.config_command == CLICommands.CONFIG_INIT:
                if args.force:
                    config = config_manager.reset_config()
                    print(Messages.Success.CONFIG_RESET)
                else:
                    config = config_manager.get_config()
                    print(Messages.Success.CONFIG_INITIALIZED)

                print(f"  Storage: {config.storage_path}")
                print(f"  Backups: {config.backup_path}")
                print(f"  Config: {config_manager.config_file}")

            elif args.config_command == CLICommands.CONFIG_SET:
                try:
                    # Convert value to appropriate type
                    value = args.value
                    if args.key in INTEGER_CONFIG_KEYS:
                        value = int(value)
                    elif args.key in BOOLEAN_CONFIG_KEYS:
                        value = value.lower() in BOOLEAN_TRUE_VALUES

                    config = config_manager.update_config(**{args.key: value})
                    print(Messages.Success.CONFIG_UPDATED.format(args.key, value))
                except Exception as e:
                    print(Messages.Error.CONFIG_UPDATE_FAILED.format(e), file=sys.stderr)
                    return 1

            else:
                config_parser.print_help()
                return 1

        elif args.command == "export":
            itinerary_id = UUID(args.id)
            itinerary = manager.get_itinerary(itinerary_id)

            if not itinerary:
                print(f"Itinerary {args.id} not found.", file=sys.stderr)
                return 1

            output_path = Path(args.output)

            if args.format == "markdown":
                markdown_content = _export_to_markdown(itinerary)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
            else:  # json
                with open(output_path, 'w') as f:
                    json.dump(itinerary.model_dump(mode='json'), f, indent=2, default=str)

            print(f"Exported itinerary ({args.format}) to: {output_path}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


def _export_to_markdown(itinerary) -> str:
    """Export an itinerary to markdown format."""
    from datetime import timedelta

    # Calculate duration
    duration = (itinerary.end_date - itinerary.start_date).days + 1

    # Build markdown content
    lines = []

    # YAML Front Matter
    lines.append("---")
    lines.append(f"created_date: '{itinerary.created_at.date().isoformat()}'")
    lines.append(f"last_modified: '{itinerary.updated_at.date().isoformat()}'")
    lines.append(f"slug: '{itinerary.title.lower().replace(' ', '-')}'")
    lines.append(f"status: {itinerary.status.lower()}")
    lines.append(f"title: '{itinerary.title}'")
    lines.append("type: itinerary")
    lines.append(f"duration: '{duration} Days'")

    # Destinations
    if itinerary.destinations:
        dest_names = [dest.name for dest in itinerary.destinations]
        lines.append(f"destinations: {dest_names}")
    elif itinerary.segments:
        # Extract destinations from segments
        dest_names = set()
        for segment in itinerary.segments:
            if hasattr(segment, 'destination') and segment.destination:
                dest_names.add(segment.destination.name)
            elif hasattr(segment, 'location') and segment.location:
                dest_names.add(segment.location.name)
        if dest_names:
            lines.append(f"destinations: {list(dest_names)}")

    lines.append(f"trip_style: '{itinerary.trip_type or 'Mixed'}'")
    lines.append(f"best_season: '{itinerary.start_date.strftime('%B')} - {itinerary.end_date.strftime('%B')}'")
    lines.append("---")
    lines.append("")

    # Header Section
    lines.append(f"# {duration} Days {itinerary.title}")
    lines.append("")

    # Destinations line
    if itinerary.destinations:
        dest_line = " • ".join([dest.name for dest in itinerary.destinations])
        lines.append(dest_line)
        lines.append("")

    # Trip info
    trip_info = f"**Trip Type:** {itinerary.trip_type or 'Mixed'} | **Duration:** {duration} Days"
    if itinerary.start_date and itinerary.end_date:
        trip_info += f" | **Dates:** {itinerary.start_date.strftime('%B %d, %Y')} - {itinerary.end_date.strftime('%B %d, %Y')}"
    lines.append(trip_info)
    lines.append("")

    # Description
    if itinerary.description:
        lines.append("## Trip Overview")
        lines.append("")
        lines.append(itinerary.description)
        lines.append("")

    # Travelers
    if itinerary.travelers:
        lines.append("## Travelers")
        lines.append("")
        for traveler in itinerary.travelers:
            name = f"{traveler.first_name} {traveler.last_name}"
            if traveler.middle_name:
                name = f"{traveler.first_name} {traveler.middle_name} {traveler.last_name}"
            lines.append(f"- **{name}** ({traveler.type})")
            if traveler.email:
                lines.append(f"  - Email: {traveler.email}")
            if traveler.phone:
                lines.append(f"  - Phone: {traveler.phone}")
            if traveler.special_requests:
                lines.append(f"  - Special Requests: {', '.join(traveler.special_requests)}")
        lines.append("")

    # Segments by day
    if itinerary.segments:
        lines.append("## Itinerary")
        lines.append("")

        # Group segments by date
        segments_by_date = {}
        for segment in itinerary.segments:
            segment_date = segment.start_datetime.date()
            if segment_date not in segments_by_date:
                segments_by_date[segment_date] = []
            segments_by_date[segment_date].append(segment)

        # Sort by date
        for segment_date in sorted(segments_by_date.keys()):
            day_segments = segments_by_date[segment_date]
            day_num = (segment_date - itinerary.start_date).days + 1

            lines.append(f"### Day {day_num} - {segment_date.strftime('%A, %B %d, %Y')}")
            lines.append("")

            # Sort segments by time
            day_segments.sort(key=lambda s: s.start_datetime)

            for segment in day_segments:
                lines.append(_format_segment_markdown(segment))
                lines.append("")

    # Financial Summary
    if itinerary.total_price or any(s.total_price for s in itinerary.segments):
        lines.append("## Financial Summary")
        lines.append("")

        if itinerary.total_price:
            lines.append(f"**Total Trip Cost:** {itinerary.total_price.currency} {itinerary.total_price.amount}")
        else:
            # Calculate from segments
            total = itinerary.calculate_total_price()
            if total:
                lines.append(f"**Total Trip Cost:** {total.currency} {total.amount}")

        # Breakdown by segment type
        segment_costs = {}
        for segment in itinerary.segments:
            if segment.total_price:
                seg_type = segment.type
                if seg_type not in segment_costs:
                    segment_costs[seg_type] = []
                segment_costs[seg_type].append(segment.total_price)

        if segment_costs:
            lines.append("")
            lines.append("**Cost Breakdown:**")
            for seg_type, costs in segment_costs.items():
                total_for_type = sum(cost.amount for cost in costs)
                currency = costs[0].currency if costs else "USD"
                lines.append(f"- {seg_type.title()}: {currency} {total_for_type}")

        lines.append("")

    # Tags and Metadata
    if itinerary.tags or itinerary.metadata:
        lines.append("## Additional Information")
        lines.append("")

        if itinerary.tags:
            lines.append(f"**Tags:** {', '.join(itinerary.tags)}")
            lines.append("")

        if itinerary.cost_center:
            lines.append(f"**Cost Center:** {itinerary.cost_center}")
        if itinerary.project_code:
            lines.append(f"**Project Code:** {itinerary.project_code}")

        if itinerary.metadata:
            lines.append("")
            lines.append("**Metadata:**")
            for key, value in itinerary.metadata.items():
                lines.append(f"- {key.title()}: {value}")

    return "\n".join(lines)


def _format_segment_markdown(segment) -> str:
    """Format a single segment as markdown."""
    lines = []

    # Time range
    start_time = segment.start_datetime.strftime('%H:%M')
    end_time = segment.end_datetime.strftime('%H:%M')

    if segment.type == "FLIGHT":
        lines.append(f"#### ✈️ Flight: {segment.flight_number} ({start_time} - {end_time})")
        lines.append(f"**{segment.airline.name}** - {segment.origin.name} → {segment.destination.name}")
        if segment.cabin:
            lines.append(f"**Cabin:** {segment.cabin}")
        if segment.confirmation_number:
            lines.append(f"**Confirmation:** {segment.confirmation_number}")

    elif segment.type == "HOTEL":
        check_in = segment.check_in_date.strftime('%B %d')
        check_out = segment.check_out_date.strftime('%B %d')
        lines.append(f"#### 🏨 Hotel: {segment.property.name}")
        lines.append(f"**Location:** {segment.location.name}")
        lines.append(f"**Dates:** {check_in} - {check_out}")
        if segment.room_type:
            lines.append(f"**Room:** {segment.room_type}")
        if segment.confirmation_number:
            lines.append(f"**Confirmation:** {segment.confirmation_number}")

    elif segment.type == "MEETING":
        lines.append(f"#### 🤝 Meeting: {segment.title} ({start_time} - {end_time})")
        lines.append(f"**Location:** {segment.location.name}")
        if segment.organizer:
            lines.append(f"**Organizer:** {segment.organizer}")
        if segment.attendees:
            lines.append(f"**Attendees:** {', '.join(segment.attendees)}")

    elif segment.type == "ACTIVITY":
        lines.append(f"#### 🎯 Activity: {segment.name} ({start_time} - {end_time})")
        lines.append(f"**Location:** {segment.location.name}")
        if segment.description:
            lines.append(f"**Description:** {segment.description}")
        if segment.voucher_number:
            lines.append(f"**Voucher:** {segment.voucher_number}")

    elif segment.type == "TRANSFER":
        lines.append(f"#### 🚗 Transfer: {segment.transfer_type} ({start_time} - {end_time})")
        lines.append(f"**Route:** {segment.pickup_location.name} → {segment.dropoff_location.name}")
        if segment.driver_name:
            lines.append(f"**Driver:** {segment.driver_name}")
            if segment.driver_phone:
                lines.append(f"**Phone:** {segment.driver_phone}")

    else:  # CUSTOM or other
        title = getattr(segment, 'title', getattr(segment, 'name', f"{segment.type} Segment"))
        lines.append(f"#### 📋 {title} ({start_time} - {end_time})")
        if hasattr(segment, 'location') and segment.location:
            lines.append(f"**Location:** {segment.location.name}")
        if hasattr(segment, 'description') and segment.description:
            lines.append(f"**Description:** {segment.description}")

    # Common fields
    if segment.total_price:
        lines.append(f"**Cost:** {segment.total_price.currency} {segment.total_price.amount}")

    if segment.notes:
        lines.append(f"**Notes:** {segment.notes}")

    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())