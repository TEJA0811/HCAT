import { Injectable } from '@nestjs/common';
import { CreateProjectDto } from './dto/create-project.dto';
import { UpdateProjectDto } from './dto/update-project.dto';
import { InjectRepository } from '@nestjs/typeorm';
import { Project } from './entities/project.entity';
import { Repository, In } from 'typeorm';
import { Manager } from '../managers/entities/manager.entity';
import { User } from '../users/entities/user.entity';
import { Team } from '../teams/entities/team.entity';

@Injectable()
export class ProjectsService {
  constructor(
    @InjectRepository(Project)
    private readonly projectRepository: Repository<Project>,
     @InjectRepository(Manager)
    private readonly managerRepository: Repository<Manager>,
     @InjectRepository(User)
    private readonly userRepository: Repository<User>,
     @InjectRepository(Team)
    private readonly teamRepository: Repository<Team>,
  ) {}

  async create(createProjectDto: CreateProjectDto): Promise<Project> {
  // Check if project with this name already exists
  const existingProject = await this.projectRepository.findOne({
    where: { name: createProjectDto.name },
    relations: ['managers', 'users'],
  });

  if (existingProject) {
    // Project exists, add new managers and users to it
    const managersToAdd: Manager[] = [];
    const usersToAdd: User[] = [];

    // Get new managers if provided
    if (createProjectDto.manager_ids && createProjectDto.manager_ids.length > 0) {
      const newManagers = await this.managerRepository.find({
        where: { id: In(createProjectDto.manager_ids) },
      });

      // Get existing manager IDs
      const existingManagerIds = existingProject.managers.map(m => m.id);

      // Filter out managers that are already assigned
      managersToAdd.push(
        ...newManagers.filter(m => !existingManagerIds.includes(m.id))
      );
    }

    // // Get new users if provided
    // if (createProjectDto.user_ids && createProjectDto.user_ids.length > 0) {
    //   const newUsers = await this.userRepository.find({
    //     where: { id: In(createProjectDto.user_ids) },
    //   });

    //   // Get existing user IDs
    //   const existingUserIds = existingProject.users.map(u => u.id);

    //   // Filter out users that are already assigned
    //   usersToAdd.push(
    //     ...newUsers.filter(u => !existingUserIds.includes(u.id))
    //   );
    // }

    // Add new managers and users
    existingProject.managers = [...existingProject.managers, ...managersToAdd];
    // existingProject.users = [...existingProject.users, ...usersToAdd];

    return await this.projectRepository.save(existingProject);
  }

  // Project doesn't exist, create new one
  const project = this.projectRepository.create({
    name: createProjectDto.name,
    description: createProjectDto.description,
    start_date: createProjectDto.start_date,
    end_date: createProjectDto.end_date,
    status: createProjectDto.status,
  });

  // Assign managers
  if (createProjectDto.manager_ids && createProjectDto.manager_ids.length > 0) {
    project.managers = await this.managerRepository.find({
      where: { id: In(createProjectDto.manager_ids) },
    });
  }

  // // Assign users
  // if (createProjectDto.user_ids && createProjectDto.user_ids.length > 0) {
  //   project.users = await this.userRepository.find({
  //     where: { id: In(createProjectDto.user_ids) },
  //   });
  // }

  return await this.projectRepository.save(project);
}

async findAll(): Promise<Project[]> {
  return await this.projectRepository.find({
    relations: ['managers', 'users'],
  });
}

  async findBy(query: object) {
    return await Project.findOne(query);
  }

  async update(id: number, updateProjectDto: UpdateProjectDto) {
    await Project.update({ id }, updateProjectDto);
    return await Project.findOneBy({ id });
  }

  async remove(id: number) {
    await Project.delete({ id });
    return { deleted: true };
  }


// Get project with all managers and users
async findOne(id: number): Promise<Project | null> {
  return await this.projectRepository.findOne({
    where: { id },
    relations: ['managers', 'users'],
  });
}





}
