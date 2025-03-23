import os
import requests
import csv
import time
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog


class CanvasAPI:
    def __init__(self, api_token, base_url):
        self.api_token = api_token
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {self.api_token}'}
        self.course_id = None

    def fetch_all_pages(self, url):
        data = []
        while url:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data.extend(response.json())
            url = response.links.get('next', {}).get('url')
        return data

    """Josh doesn't really like this idea.
    Imma still leave it in here for now, but i'll write another method
    that will be used to get the list of active courses.
    """
    def get_course_by_id(self, course_id):
        url = f'{self.base_url}courses/{course_id}'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_active_courses(self, enrollment_state='active'):
        """Fetch courses the user is actively enrolled in and dynamically filter only those still active."""
        params = {'enrollment_state': enrollment_state}
        url = f'{self.base_url}courses'
        courses = self.fetch_all_pages(url)

        # Filter dynamically for courses that are not concluded or deleted
        current_courses = [
            course for course in courses
            if course.get('workflow_state') == 'available'  # Ensure the course is available (not completed, deleted, etc.)
            and not course.get('end_at')  # Ignore courses with an end date already passed
        ]
        return current_courses


    def get_assignments(self, course_id):
        url = f'{self.base_url}courses/{course_id}/assignments'
        return self.fetch_all_pages(url)

    def get_assignment_details(self, course_id, assignment_id):
        url = f'{self.base_url}courses/{course_id}/assignments/{assignment_id}'
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_submissions(self, course_id, assignment_id):
        url = f'{self.base_url}courses/{course_id}/assignments/{assignment_id}/submissions'
        return self.fetch_all_pages(url)

    def get_groups(self, course_id):
        url = f'{self.base_url}courses/{course_id}/groups'
        return self.fetch_all_pages(url)

    def get_group_members(self, group_id):
        url = f'{self.base_url}groups/{group_id}/users'
        return self.fetch_all_pages(url)

    def write_groups_to_csv(self, course_id):
        csv_path = 'groups_and_members.csv'
        if os.path.exists(csv_path):
            print(f"'{csv_path}' already exists. Skipping download of groups and members.")
            return

        groups = self.get_groups(course_id)
        with open(csv_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Group Name', 'Group ID', 'Member Name', 'Member ID'])
            for group in groups:
                group_id = group['id']
                group_name = group['name']
                members = self.get_group_members(group_id)
                for member in members:
                    member_name = member['name']
                    member_id = member['id']
                    csvwriter.writerow([group_name, group_id, member_name, member_id])
        print(f"Groups and members have been written to '{csv_path}'.")


    def load_names_from_csv(self, csv_path='groups_and_members.csv'):
        student_names = {}
        group_names = {}
        group_members = {}
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                group_id = row['Group ID']
                student_id = row['Member ID']
                group_names[group_id] = row['Group Name']
                student_names[student_id] = row['Member Name']
                if group_id not in group_members:
                    group_members[group_id] = []
                group_members[group_id].append(student_id)
        return student_names, group_names, group_members

    def wait_for_downloads(self, directory, filename, timeout=60):
        file_path = os.path.join(directory, filename)
        print(f"Waiting for download to complete: {file_path}")
        start_time = time.time()
        while True:
            if os.path.isfile(file_path):
                # Check if the file's modification time has stopped changing
                initial_mtime = os.path.getmtime(file_path)
                time.sleep(1)
                if os.path.getmtime(file_path) == initial_mtime:
                    print(f"Download complete: {file_path}")
                    return
            if time.time() - start_time > timeout:
                print(f"Timeout waiting for download: {file_path}")
                return
            time.sleep(1)

    def download_submission(self, submission_url, dest_path):
        response = requests.get(submission_url, headers=self.headers)
        response.raise_for_status()
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, 'wb') as file:
            file.write(response.content)
        self.wait_for_downloads(os.path.dirname(dest_path), os.path.basename(dest_path))


def main():
    # Replace 'YOUR_API_TOKEN' with your actual Canvas LMS API token 
    API_TOKEN = 'YOUR_API_TOKEN' 
    BASE_URL = 'https://learn.ontariotechu.ca/api/v1/'
    
    # Setup tkinter root window (hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    # Fetch only active courses
    print("Fetching active courses...")
    canvas_api = CanvasAPI(API_TOKEN, BASE_URL)
    active_courses = canvas_api.get_active_courses()

    if not active_courses:
        print("No active courses found.")
        return

    # Display a list of active courses
    print("Active Courses with names:")
    for index, course in enumerate(active_courses, start=1):
        course_name = course.get("name")
        if course_name and course_name != "Unnamed Course":
            course_id = course["id"]
            print(f"{index}. {course_name} (ID: {course_id})")

    # Let the user select a course
    selected_course = input("Enter the number of the course you want to use: ")
    selected_course_id = active_courses[int(selected_course) - 1]["id"]
    selected_course_name = active_courses[int(selected_course) - 1].get("name", "Unnamed Course")
    print(f"Using course: {selected_course_name} (ID: {selected_course_id})")

    # Prompt user to select a destination folder
    print("Select a destination folder to save submissions...")
    destination_folder = filedialog.askdirectory()
    if not destination_folder:
        print("No folder selected. Exiting.")
        return
    print(f"Selected destination folder: {destination_folder}")

    # Fetch groups and assignments
    canvas_api.write_groups_to_csv(selected_course_id)
    print("Groups and members have been written to 'groups_and_members.csv'.")
    
    student_names, group_names, group_members = canvas_api.load_names_from_csv()
    assignments = canvas_api.get_assignments(selected_course_id)

    # Display available assignments
    print("Assignments:")
    for index, assignment in enumerate(assignments, start=1):
        print(f'{index}. {assignment["name"]} (ID: {assignment["id"]})')

    selected_assignment = input("Enter the number of the assignment you want to inspect: ")
    selected_assignment_id = assignments[int(selected_assignment) - 1]["id"]

    # Determine if the assignment is group-based
    assignment_details = canvas_api.get_assignment_details(selected_course_id, selected_assignment_id)
    is_group_assignment = assignment_details.get('group_category_id') is not None

    if is_group_assignment:
        submission_type = input("The selected assignment is configured for group submissions. Do you want to view group or individual submissions? Enter '(G)roup' or '(I)ndividual': ").strip().lower()
    else:
        submission_type = 'i'
        print(f"The selected assignment is configured for individual submissions.")

    download_submissions = input("Do you want to download the submissions if found? Enter '(Y)es' or '(N)o': ").strip().lower()

    # Fetch submissions for the assignment
    print("\nSubmissions:")
    submissions = canvas_api.get_submissions(selected_course_id, selected_assignment_id)

    submission_status_counts = defaultdict(int)
    submitted_groups = set()
    submitted_students = set()

    if submission_type == 'g':  # Group-based logic
        total_groups = len(group_names)
        sorted_group_ids = sorted(group_names.keys(), key=lambda x: int(x))

        for group_id in sorted_group_ids:
            if group_id in submitted_groups:  # Skip already processed groups
                continue

            group_name = group_names[group_id]
            print(f"\nProcessing Group: {group_name} (ID: {group_id})")

            # Use the first member of the group to fetch the submission
            first_member_id = group_members[group_id][0]  # Get the first member's student ID
            group_submissions = [
                submission for submission in submissions
                if str(submission['user_id']) == first_member_id
            ]

            if group_submissions:  # Process the first submission for the group
                submission = group_submissions[0]
                submission_status = submission['workflow_state']
                submission_status_counts[submission_status] += 1

                if submission_status != 'unsubmitted':
                    if download_submissions == 'y':
                        attachments = submission.get('attachments', [])
                        if attachments:
                            for attachment in attachments:
                                submission_url = attachment.get('url')
                                original_filename = attachment.get('filename')
                                if submission_url and original_filename:
                                    dest_path = os.path.join(
                                        destination_folder,
                                        group_name,
                                        original_filename  # Use the original filename only
                                    )
                                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                                    canvas_api.download_submission(submission_url, dest_path)
                                    print(f'Downloaded submission file {original_filename} for {group_name}')
                        else:
                            print(f"No attachments found for group {group_name}")
                    else:
                        print(f"Group {group_name}'s submission found but not downloaded.")
            else:
                print(f"No submissions found for group {group_name}")

            # Mark the group as processed
            submitted_groups.add(group_id)

        # Validation for group processing
        print("\nValidation Check:")
        print(f"Total groups expected: {total_groups}")
        print(f"Total groups processed: {len(submitted_groups)}")
        if len(submitted_groups) != total_groups:
            missing_groups = set(group_names.keys()) - submitted_groups
            print(f"Warning: Some groups were not fully processed. Missing groups: {missing_groups}")
        else:
            print("All groups have been processed successfully!")

    elif submission_type == 'i':  # Individual-based logic
        processed_students = set()
        total_students = len(student_names)
        for submission in submissions:
            student_id = str(submission['user_id'])
            if student_id in submitted_students:  # Skip already processed students
                continue

            student_name = student_names.get(student_id, f"Student {student_id}")
            submission_status = submission['workflow_state']
            submission_status_counts[submission_status] += 1

            # Process valid submissions
            if submission_status != 'unsubmitted':
                if download_submissions == 'y':
                    attachments = submission.get('attachments', [])
                    if attachments:
                        for attachment in attachments:
                            submission_url = attachment.get('url')
                            original_filename = attachment.get('filename')
                            if submission_url and original_filename:
                                dest_path = os.path.join(
                                    destination_folder,
                                    student_name,
                                    original_filename  # Use the original filename only
                                )
                                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                                canvas_api.download_submission(submission_url, dest_path)
                                print(f'Downloaded submission file {original_filename} for {student_name}')
                    else:
                        print(f"No attachments found for student {student_name}")
                else:
                    print(f"Student {student_name}'s submission found but not downloaded.")

            # Mark the student as processed
            submitted_students.add(student_id)

        # Validation for student processing
        print("\nValidation Check:")
        print(f"Total students expected: {total_students}")
        print(f"Total students processed: {len(submitted_students)}")
        if len(processed_students) != total_students:
            missing_students = set(student_names.keys()) - processed_students
            print(f"Warning: Some students were not fully processed. Missing students: {missing_students}")
        else:
            print("All students have been processed successfully!")

    # Print Summary
    print("\nSummary:")
    for status, count in submission_status_counts.items():
        print(f'{status.capitalize()} submissions: {count}')
    print(f"Total students with submissions: {len(submitted_students)}")
    print(f"Total groups with submissions: {len(submitted_groups)}")


if __name__ == '__main__':
    main()