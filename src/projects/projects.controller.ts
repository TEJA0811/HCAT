import {
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  Delete,
  ConflictException,
  Put,
} from '@nestjs/common';
import { ProjectsService } from './projects.service';
import { CreateProjectDto } from './dto/create-project.dto';
import { UpdateProjectDto } from './dto/update-project.dto';

@Controller('projects')
export class ProjectsController {
  constructor(private readonly projectsService: ProjectsService) {}

  @Post('create')
  async create(@Body() createProjectDto: CreateProjectDto) {
    const startDate = new Date(createProjectDto.start_date);
    const endDate = new Date(createProjectDto.end_date);

    if (endDate <= startDate) {
      throw new ConflictException('End date must be after start date');
    }

    const project = await this.projectsService.create(createProjectDto);
    return {
      message: 'project added',
      data: project,
    };
  }

  @Get()
  async findAll() {
    const project = await this.projectsService.findAll();
    return {
      message: 'project list',
      data: project,
    };
  }


  @Get(':id')
  async findOne(@Param('id') id: string) {
    const project = await this.projectsService.findOne(+id);
    if (!project) {
      return {
        message: 'project not found',
        data: {},
      };
    }
    return {
      message: 'project found',
      data: project,
    };
  }

  @Put(':id')
  async update(
    @Param('id') id: string,
    @Body() updateProjectDto: UpdateProjectDto,
  ) {
    // First, check if the project exists
    const project = await this.projectsService.findOne(+id);

    if (!project) {
      return {
        message: 'project not found',
        data: {},
      };
    }

    // Only check for duplicate name if the name is being updated and it's different
    if (updateProjectDto.name && updateProjectDto.name !== project.name) {
      const existingproject = await this.projectsService.findBy({
        where: { name: updateProjectDto.name },
      });

      if (existingproject) {
        throw new ConflictException('Project with this name already exists');
      }
    }

    // Validate dates if both are provided
    if (updateProjectDto.start_date && updateProjectDto.end_date) {
      const startDate = new Date(updateProjectDto.start_date);
      const endDate = new Date(updateProjectDto.end_date);

      if (endDate <= startDate) {
        throw new ConflictException('End date must be after start date');
      }
    }

    const updatedproject = await this.projectsService.update(
      +id,
      updateProjectDto,
    );

    return {
      message: 'Project updated successfully',
      data: updatedproject,
    };
  }

  @Delete(':id')
  async remove(@Param('id') id: string) {
    const project = await this.projectsService.findOne(+id);

    if (!project) {
      return {
        message: 'project not found',
        data: {},
      };
    }

    await this.projectsService.remove(+id);

    return {
      message: 'project deleted successfully',
      data: project,
    };
  }
}
