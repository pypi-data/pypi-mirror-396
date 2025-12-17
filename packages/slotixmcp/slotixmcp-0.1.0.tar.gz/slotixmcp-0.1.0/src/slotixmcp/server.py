"""
MCP Server for Slotix.

This server provides tools for managing appointments, clients, and notifications
through AI assistants like Claude Desktop and ChatGPT.
"""
import asyncio
import json
from datetime import datetime, date
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .client import SlotixClient


# Initialize MCP server
server = Server("slotix")
client: SlotixClient | None = None


def get_client() -> SlotixClient:
    """Get or create the Slotix client."""
    global client
    if client is None:
        client = SlotixClient()
    return client


def format_datetime(dt_str: str) -> str:
    """Format datetime string for display."""
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return dt_str


def format_date(d_str: str) -> str:
    """Format date string for display."""
    try:
        d = date.fromisoformat(d_str)
        return d.strftime("%d/%m/%Y")
    except Exception:
        return d_str


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_profile",
            description="Get your professional profile information including business name, contact details, and settings.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_appointments",
            description="Get appointments within a date range. Default: next 7 days. Use filters for specific dates or status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD). Default: today"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD). Default: start_date + 7 days"
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by status: booked, completed, cancelled, no_show",
                        "enum": ["booked", "completed", "cancelled", "no_show"]
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_today_appointments",
            description="Get all appointments scheduled for today.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_week_appointments",
            description="Get all appointments for the current week (Monday to Sunday).",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_appointment",
            description="Get details of a specific appointment by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": "The appointment ID"
                    }
                },
                "required": ["appointment_id"]
            }
        ),
        Tool(
            name="create_appointment",
            description="Create a new appointment for a client.",
            inputSchema={
                "type": "object",
                "properties": {
                    "client_name": {
                        "type": "string",
                        "description": "Client's name"
                    },
                    "start_datetime": {
                        "type": "string",
                        "description": "Appointment date and time (ISO 8601 format, e.g., 2024-12-20T10:00:00)"
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Duration in minutes (default: 30)",
                        "default": 30
                    },
                    "client_contact": {
                        "type": "string",
                        "description": "Client's contact (email or phone)"
                    },
                    "client_id": {
                        "type": "integer",
                        "description": "Existing client ID (optional)"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Notes for the appointment"
                    }
                },
                "required": ["client_name", "start_datetime"]
            }
        ),
        Tool(
            name="update_appointment",
            description="Update an existing appointment (reschedule, add notes, change status).",
            inputSchema={
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": "The appointment ID to update"
                    },
                    "start_datetime": {
                        "type": "string",
                        "description": "New date and time (ISO 8601 format)"
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "New duration in minutes"
                    },
                    "status": {
                        "type": "string",
                        "description": "New status: booked, completed, cancelled, no_show",
                        "enum": ["booked", "completed", "cancelled", "no_show"]
                    },
                    "notes": {
                        "type": "string",
                        "description": "Updated notes"
                    }
                },
                "required": ["appointment_id"]
            }
        ),
        Tool(
            name="cancel_appointment",
            description="Cancel an appointment. The appointment will be marked as cancelled (not deleted).",
            inputSchema={
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": "The appointment ID to cancel"
                    }
                },
                "required": ["appointment_id"]
            }
        ),
        Tool(
            name="reschedule_appointment",
            description="Reschedule an appointment to a new date/time and optionally notify the client.",
            inputSchema={
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "integer",
                        "description": "The appointment ID to reschedule"
                    },
                    "new_datetime": {
                        "type": "string",
                        "description": "New date and time (ISO 8601 format)"
                    },
                    "notify_client": {
                        "type": "boolean",
                        "description": "Send notification to client about the change",
                        "default": True
                    },
                    "message": {
                        "type": "string",
                        "description": "Custom message to send to client (optional)"
                    }
                },
                "required": ["appointment_id", "new_datetime"]
            }
        ),
        Tool(
            name="get_clients",
            description="Get list of clients. Optionally search by name, email, or phone.",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search term (name, email, or phone)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of clients to return (default: 50)",
                        "default": 50
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_client",
            description="Get detailed information about a specific client including appointment history.",
            inputSchema={
                "type": "object",
                "properties": {
                    "client_id": {
                        "type": "integer",
                        "description": "The client ID"
                    }
                },
                "required": ["client_id"]
            }
        ),
        Tool(
            name="get_availability",
            description="Get available time slots for booking appointments.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD). Default: today"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD). Default: start_date + 7 days"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_stats",
            description="Get business statistics (appointments, revenue, clients) for a time period.",
            inputSchema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "description": "Time period: today, week, month, year",
                        "enum": ["today", "week", "month", "year"],
                        "default": "month"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="send_notification",
            description="Send a message to a client via Telegram or WhatsApp.",
            inputSchema={
                "type": "object",
                "properties": {
                    "client_id": {
                        "type": "integer",
                        "description": "The client ID to send the message to"
                    },
                    "message": {
                        "type": "string",
                        "description": "The message to send"
                    },
                    "channel": {
                        "type": "string",
                        "description": "Communication channel: telegram, whatsapp, or auto (tries both)",
                        "enum": ["telegram", "whatsapp", "auto"],
                        "default": "auto"
                    }
                },
                "required": ["client_id", "message"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        slotix = get_client()
        result: Any = None

        if name == "get_profile":
            result = await slotix.get_profile()
            text = f"""**Profile**
- Name: {result.get('full_name', 'N/A')}
- Business: {result.get('business_name', 'N/A')}
- Email: {result.get('email', 'N/A')}
- Phone: {result.get('phone', 'N/A')}
- Timezone: {result.get('timezone', 'N/A')}
- Currency: {result.get('currency', 'N/A')}
- Default slot duration: {result.get('default_slot_duration', 30)} minutes
- Telegram bot: {'Active' if result.get('telegram_bot_active') else 'Inactive'}
- WhatsApp: {'Active' if result.get('whatsapp_active') else 'Inactive'}"""

        elif name == "get_appointments":
            result = await slotix.get_appointments(
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date"),
                status=arguments.get("status")
            )
            appointments = result.get("appointments", [])
            if not appointments:
                text = f"No appointments found for {result.get('date_range', 'the selected period')}."
            else:
                text = f"**Appointments** ({result.get('date_range', '')})\n\n"
                for apt in appointments:
                    text += f"- **{apt['client_name']}** - {format_datetime(apt['start_datetime'])} ({apt['duration_minutes']}min) - {apt['status']}\n"
                    if apt.get('notes'):
                        text += f"  Notes: {apt['notes']}\n"
                text += f"\nTotal: {result.get('total', len(appointments))} appointments"

        elif name == "get_today_appointments":
            result = await slotix.get_today_appointments()
            appointments = result.get("appointments", [])
            if not appointments:
                text = "No appointments scheduled for today."
            else:
                text = "**Today's Appointments**\n\n"
                for apt in appointments:
                    text += f"- **{apt['client_name']}** - {format_datetime(apt['start_datetime'])} ({apt['duration_minutes']}min) - {apt['status']}\n"
                text += f"\nTotal: {len(appointments)} appointments"

        elif name == "get_week_appointments":
            result = await slotix.get_week_appointments()
            appointments = result.get("appointments", [])
            if not appointments:
                text = "No appointments scheduled for this week."
            else:
                text = f"**This Week's Appointments** ({result.get('date_range', '')})\n\n"
                for apt in appointments:
                    text += f"- **{apt['client_name']}** - {format_datetime(apt['start_datetime'])} ({apt['duration_minutes']}min) - {apt['status']}\n"
                text += f"\nTotal: {len(appointments)} appointments"

        elif name == "get_appointment":
            result = await slotix.get_appointment(arguments["appointment_id"])
            text = f"""**Appointment #{result['id']}**
- Client: {result['client_name']}
- Contact: {result.get('client_contact', 'N/A')}
- Date: {format_datetime(result['start_datetime'])} - {format_datetime(result['end_datetime'])}
- Duration: {result['duration_minutes']} minutes
- Status: {result['status']}
- Source: {result['source']}
- Notes: {result.get('notes', 'None')}
- Total: {result.get('total_price', 'N/A')}"""

        elif name == "create_appointment":
            result = await slotix.create_appointment(
                client_name=arguments["client_name"],
                start_datetime=arguments["start_datetime"],
                duration_minutes=arguments.get("duration_minutes", 30),
                client_contact=arguments.get("client_contact"),
                client_id=arguments.get("client_id"),
                notes=arguments.get("notes")
            )
            text = f"""**Appointment Created**
- ID: {result['id']}
- Client: {result['client_name']}
- Date: {format_datetime(result['start_datetime'])}
- Duration: {result['duration_minutes']} minutes
- Status: {result['status']}"""

        elif name == "update_appointment":
            result = await slotix.update_appointment(
                appointment_id=arguments["appointment_id"],
                start_datetime=arguments.get("start_datetime"),
                duration_minutes=arguments.get("duration_minutes"),
                status=arguments.get("status"),
                notes=arguments.get("notes")
            )
            text = f"""**Appointment Updated**
- ID: {result['id']}
- Client: {result['client_name']}
- Date: {format_datetime(result['start_datetime'])}
- Duration: {result['duration_minutes']} minutes
- Status: {result['status']}"""

        elif name == "cancel_appointment":
            result = await slotix.cancel_appointment(arguments["appointment_id"])
            text = f"**Appointment #{arguments['appointment_id']} cancelled.**"

        elif name == "reschedule_appointment":
            # First update the appointment
            result = await slotix.update_appointment(
                appointment_id=arguments["appointment_id"],
                start_datetime=arguments["new_datetime"]
            )
            text = f"""**Appointment Rescheduled**
- ID: {result['id']}
- Client: {result['client_name']}
- New Date: {format_datetime(result['start_datetime'])}"""

            # Optionally notify the client
            if arguments.get("notify_client", True) and result.get("client_id"):
                message = arguments.get("message") or f"Your appointment has been rescheduled to {format_datetime(result['start_datetime'])}."
                try:
                    notify_result = await slotix.send_notification(
                        client_id=result["client_id"],
                        message=message
                    )
                    if notify_result.get("success"):
                        text += f"\n\nClient notified via {notify_result.get('channel_used', 'messaging')}."
                    else:
                        text += f"\n\nNote: Could not notify client - {notify_result.get('message', 'unknown error')}"
                except Exception as e:
                    text += f"\n\nNote: Could not notify client - {str(e)}"

        elif name == "get_clients":
            result = await slotix.get_clients(
                search=arguments.get("search"),
                limit=arguments.get("limit", 50)
            )
            clients = result.get("clients", [])
            if not clients:
                text = "No clients found."
            else:
                text = "**Clients**\n\n"
                for c in clients:
                    text += f"- **{c['full_name']}** (ID: {c['id']})"
                    if c.get('phone'):
                        text += f" - {c['phone']}"
                    if c.get('email'):
                        text += f" - {c['email']}"
                    text += f" - {c['total_appointments']} appointments"
                    if c.get('is_banned'):
                        text += " [BANNED]"
                    text += "\n"
                text += f"\nTotal: {result.get('total', len(clients))} clients"

        elif name == "get_client":
            result = await slotix.get_client(arguments["client_id"])
            text = f"""**Client #{result['id']}**
- Name: {result['full_name']}
- Email: {result.get('email', 'N/A')}
- Phone: {result.get('phone', 'N/A')}
- Telegram: {result.get('telegram_username', 'N/A')}
- Total Appointments: {result['total_appointments']}
- Total Spent: {result['total_spent']}
- Notes: {result.get('notes', 'None')}
- Status: {'BANNED' if result.get('is_banned') else 'Active'}"""

        elif name == "get_availability":
            result = await slotix.get_availability(
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date")
            )
            if not result:
                text = "No available slots found for the selected period."
            else:
                text = "**Available Slots**\n\n"
                for day in result:
                    text += f"**{format_date(day['date'])}**\n"
                    for slot in day.get("slots", []):
                        text += f"  - {slot['start_time']} - {slot['end_time']} ({slot['duration_minutes']}min)\n"
                    text += "\n"

        elif name == "get_stats":
            period = arguments.get("period", "month")
            result = await slotix.get_stats(period=period)
            text = f"""**Statistics ({result.get('period', period).capitalize()})**
- Total Appointments: {result['total_appointments']}
  - Completed: {result['completed_appointments']}
  - Cancelled: {result['cancelled_appointments']}
  - No-shows: {result['no_show_appointments']}
- Total Revenue: {result['total_revenue']}
- Avg. Appointment Value: {result.get('average_appointment_value', 'N/A')}
- Total Clients: {result['total_clients']}
- New Clients: {result['new_clients']}"""

        elif name == "send_notification":
            result = await slotix.send_notification(
                client_id=arguments["client_id"],
                message=arguments["message"],
                channel=arguments.get("channel", "auto")
            )
            if result.get("success"):
                text = f"**Message sent** via {result.get('channel_used', 'messaging')}."
            else:
                text = f"**Failed to send message**: {result.get('message', 'Unknown error')}"

        else:
            text = f"Unknown tool: {name}"

        return [TextContent(type="text", text=text)]

    except ValueError as e:
        return [TextContent(type="text", text=f"**Error**: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"**Unexpected error**: {str(e)}")]


async def main_async():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """Entry point for the MCP server."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
